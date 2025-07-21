import asyncio
import logging
import os
from collections.abc import AsyncIterator
from pathlib import Path

import gradio as gr
import numpy as np
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import utils
from livekit.agents.voice import Agent, AgentSession
from livekit.agents.voice.avatar import AudioSegmentEnd, QueueAudioOutput
from livekit.agents.voice.events import UserInputTranscribedEvent
from livekit.agents.voice.io import TextOutput
from livekit.plugins import openai
from numpy.typing import NDArray

from bithuman import AsyncBithuman
from bithuman.utils import FPSController
from fastrtc import (
    AsyncAudioVideoStreamHandler,
    AudioEmitType,
    Stream,
    VideoEmitType,
    wait_for_item,
)

load_dotenv()

logger = logging.getLogger("bithuman-agent-example")
logging.basicConfig(level=logging.INFO)
logging.getLogger("livekit").setLevel(logging.DEBUG)


MODEL_ROOT = os.getenv("BITHUMAN_MODEL_ROOT")
if MODEL_ROOT is None:
    raise ValueError("BITHUMAN_MODEL_ROOT is not set")

## To use the STT, LLM and TTS agents, uncomment the following code
# from livekit.agents.llm import function_tool
# from livekit.plugins import cartesia, deepgram, openai, silero

# class EchoAgent(Agent):
#     def __init__(self) -> None:
#         super().__init__(
#             instructions="You are Echo.",
#             stt=deepgram.STT(),
#             llm=openai.LLM(model="gpt-4o-mini"),
#             tts=cartesia.TTS(),
#             vad=silero.VAD.load(),
#         )

#     async def on_enter(self):
#         self.session.generate_reply()

#     @function_tool
#     async def talk_to_alloy(self):
#         """Called when want to talk to Alloy."""
#         return AlloyAgent(), "Transferring you to Alloy."


# OpenAI realtime API agent
class AlloyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are Alloy.",
            llm=openai.realtime.RealtimeModel(voice="alloy"),
        )

    async def on_enter(self):
        self.session.generate_reply()


class BitHumanHandler(AsyncAudioVideoStreamHandler):
    avatar_name_to_file = {
        "einstein": str((Path(MODEL_ROOT) / "einstein.imx").resolve()),
        "dog": str((Path(MODEL_ROOT) / "dog.imx").resolve()),
        "companion": str((Path(MODEL_ROOT) / "companion.imx").resolve()),
    }

    def __init__(self):
        super().__init__(
            input_sample_rate=24_000,
            output_sample_rate=16_000,
            output_frame_size=320,
            fps=100,  # use a high fps to avoid lag from fastrtc frame control
        )
        # input queues
        self.input_audio_queue = asyncio.Queue[rtc.AudioFrame]()
        self.agent_audio_queue = QueueAudioOutput()
        self.agent_audio_queue._sample_rate = 16_000  # should be exposed in ctor
        self.last_text_input = ""

        # output queues
        self.video_queue = asyncio.Queue[NDArray[np.uint8]]()
        self.audio_queue = asyncio.Queue[tuple[int, NDArray[np.int16]]]()

        # bithuman runtime
        self.runtime: AsyncBithuman | None = None
        self.runtime_ready = asyncio.Event()
        self.fps_controller = FPSController(target_fps=25)

        # agent
        self.agent_session: AgentSession | None = None
        self.pushed_duration: float = 0

    @utils.log_exceptions(logger=logger)
    async def start_up(self):
        await self.wait_for_args()
        _, bithuman_api_secret, avatar_name = self.latest_args[1:]

        # setup agent
        utils.http_context._new_session_ctx()
        self.agent_session = AgentSession()
        self.agent_session.input.audio = self._agent_audio_input()
        self.agent_session.output.audio = self.agent_audio_queue
        self.agent_session.output.transcription = SimpleTextOutput()
        self.agent_session.on("user_input_transcribed", self._on_user_transcription)

        await self.agent_session.start(agent=AlloyAgent())

        # register interrupt handler
        self.agent_audio_queue.on("clear_buffer", self._on_clear_buffer)

        # setup bithuman runtime
        logger.info("loading bithuman runtime")
        self.runtime = await AsyncBithuman.create(
            api_secret=bithuman_api_secret,
            model_path=self.avatar_name_to_file[avatar_name],
        )
        await self.runtime.start()
        self.runtime_ready.set()
        logger.info("bithuman runtime ready")

        tasks = [
            self._generate_frames(),
            self._forward_audio_from_agent(),
        ]
        await asyncio.gather(*tasks)

    def _agent_audio_input(self) -> AsyncIterator[rtc.AudioFrame]:
        async def _audio_input_impl():
            while True:
                frame = await self.input_audio_queue.get()
                yield frame
                self.input_audio_queue.task_done()

        return _audio_input_impl()

    async def _generate_frames(self) -> None:
        assert self.runtime is not None

        async for frame in self.runtime.run():
            if frame.audio_chunk is not None:
                await self.audio_queue.put(
                    (frame.audio_chunk.sample_rate, frame.audio_chunk.data)
                )
                self.pushed_duration += frame.audio_chunk.duration

            if frame.has_image:
                sleep_time = self.fps_controller.wait_next_frame(sleep=False)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                await self.video_queue.put(frame.bgr_image)

                self.fps_controller.update()

            if frame.end_of_speech and self.pushed_duration > 0:
                # notify agent that audio has played
                self.agent_audio_queue.notify_playback_finished(
                    self.pushed_duration, interrupted=False
                )
                logger.info(
                    f"audio playback finished, pushed_duration={self.pushed_duration}, interrupted={False}"  # noqa: E501
                )
                self.pushed_duration = 0

    async def _forward_audio_from_agent(self) -> None:
        assert self.runtime is not None

        async for frame in self.agent_audio_queue:
            if isinstance(frame, AudioSegmentEnd):
                await self.runtime.flush()
            else:
                await self.runtime.push_audio(
                    bytes(frame.data), frame.sample_rate, last_chunk=False
                )

    def _on_clear_buffer(self) -> None:
        assert self.runtime is not None

        self.runtime.interrupt()
        if self.pushed_duration > 0:
            self.agent_audio_queue.notify_playback_finished(
                self.pushed_duration, interrupted=True
            )
            logger.info(
                f"audio playback interrupted, pushed_duration={self.pushed_duration}, interrupted={True}"  # noqa: E501
            )
            self.pushed_duration = 0

    def _on_user_transcription(self, ev: UserInputTranscribedEvent) -> None:
        print(f"User: {ev.transcript.rstrip()}[final={ev.is_final}]")

    # fastrtc hooks

    async def video_emit(self) -> VideoEmitType:
        frame = await wait_for_item(self.video_queue)
        if frame is None:
            frame = np.zeros((768, 1280, 3), dtype=np.uint8)
        else:
            self.video_queue.task_done()
        return frame

    async def video_receive(self, frame: NDArray[np.uint8]):
        pass

    async def emit(self) -> AudioEmitType:
        frame = await wait_for_item(self.audio_queue)
        if frame is not None:
            self.audio_queue.task_done()
        return frame

    async def receive(self, frame: tuple[int, NDArray[np.int16]]):
        await self.runtime_ready.wait()

        text_input: str = self.latest_args[1]
        if text_input and text_input != self.last_text_input:
            # generate text input
            self.last_text_input = text_input

            if text_input.endswith("end"):
                assert self.agent_session is not None

                text_input = text_input[:-3].strip()
                self.agent_session.interrupt()
                self.agent_session.generate_reply(user_input=text_input)
                print(f"User: {text_input}[from_text]")

        sr, array = frame
        if array.ndim == 2:
            array = array[0]  # mono

        # float32 to int16
        if array.dtype == np.float32:
            array = (array * np.iinfo(np.int16).max).astype(np.int16)

        await self.input_audio_queue.put(
            rtc.AudioFrame(
                data=array.tobytes(),
                sample_rate=sr,
                num_channels=1,
                samples_per_channel=len(array),
            )
        )

    async def shutdown(self):
        if self.runtime:
            await self.runtime.flush()
            await self.runtime.stop()

    def copy(self) -> AsyncAudioVideoStreamHandler:
        return BitHumanHandler()


class SimpleTextOutput(TextOutput):
    def __init__(self):
        super().__init__(next_in_chain=None)
        self._capturing = False

    async def capture_text(self, text: str) -> None:
        if not self._capturing:
            print("Agent: ", end="")
            self._capturing = True

        print(text, end="", flush=True)

    def flush(self) -> None:
        if self._capturing:
            print()
            self._capturing = False


stream = Stream(
    handler=BitHumanHandler(),
    mode="send-receive",
    modality="audio-video",
    additional_inputs=[
        gr.Textbox(
            label="Message", value="", info="Type what you want the avatar to say"
        ),
        gr.Textbox(
            label="API Key", type="password", value=os.getenv("BITHUMAN_API_SECRET")
        ),
        gr.Dropdown(
            choices=["einstein", "dog", "companion"],
            value="companion",
            label="Avatar",
        ),
    ],
    # send_input_on="submit",
    ui_args={"title": "Talk with a BitHuman Avatar"},
)

if __name__ == "__main__":
    stream.ui.launch()
