# Voice Driven Avatar from Audio Clip

Create an animated avatar from an audio file using bitHuman SDK. This example demonstrates the core functionality of processing audio and generating synchronized video frames.

## Overview

This example shows how to:
- Load and process audio files
- Generate avatar animations synchronized to audio
- Display the animated avatar in real-time
- Save the output as a video file
- Handle different audio formats and quality settings

## Prerequisites

- ✅ [bitHuman SDK installed](../getting-started/installation.md)
- ✅ [API credentials configured](../getting-started/validate-api.md)
- ✅ Avatar model (.imx file) downloaded
- ✅ Audio file to process (WAV, MP3, or M4A)

## Basic Implementation

### Simple Audio-to-Avatar Converter

```python
# audio_to_avatar.py
import asyncio
import os
import cv2
import numpy as np
from pathlib import Path
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk

class AudioToAvatarConverter:
    def __init__(self):
        self.runtime = None
        
    async def initialize(self):
        """Initialize the bitHuman runtime"""
        self.runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        print("✅ bitHuman runtime initialized")
    
    async def process_audio_file(self, audio_file_path: str, output_path: str = None, display_realtime: bool = True):
        """
        Process an audio file and generate avatar animation
        
        Args:
            audio_file_path: Path to input audio file
            output_path: Optional path to save video output
            display_realtime: Whether to display avatar in real-time
        """
        # Validate input file
        if not Path(audio_file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        print(f"🎵 Processing audio file: {audio_file_path}")
        
        # Load audio file
        audio_chunk = AudioChunk.from_file(audio_file_path)
        print(f"📊 Audio info: {audio_chunk.duration:.2f}s, {audio_chunk.sample_rate}Hz")
        
        # Setup video writer if saving output
        video_writer = None
        if output_path:
            video_writer = self._setup_video_writer(output_path)
        
        # Setup real-time display
        if display_realtime:
            cv2.namedWindow('bitHuman Avatar', cv2.WINDOW_AUTOSIZE)
            cv2.resizeWindow('bitHuman Avatar', 512, 512)
        
        # Process audio and generate frames
        frame_count = 0
        start_time = asyncio.get_event_loop().time()
        
        try:
            async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
                frame_count += 1
                
                # Display frame in real-time
                if display_realtime:
                    cv2.imshow('bitHuman Avatar', video_frame.image)
                    
                    # Check for exit key
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("⏹️ Stopped by user")
                        break
                
                # Save frame to video
                if video_writer:
                    video_writer.write(video_frame.image)
                
                # Progress update every 25 frames (1 second at 25fps)
                if frame_count % 25 == 0:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    progress = (frame_count / 25.0) / audio_chunk.duration * 100
                    print(f"⏳ Progress: {progress:.1f}% ({frame_count} frames, {elapsed:.1f}s)")
        
        except KeyboardInterrupt:
            print("⏹️ Processing interrupted by user")
        
        finally:
            # Cleanup
            if display_realtime:
                cv2.destroyAllWindows()
            
            if video_writer:
                video_writer.release()
                print(f"💾 Video saved to: {output_path}")
            
            total_time = asyncio.get_event_loop().time() - start_time
            fps = frame_count / total_time if total_time > 0 else 0
            
            print(f"✅ Processing complete:")
            print(f"   📹 Generated {frame_count} frames")
            print(f"   ⏱️ Total time: {total_time:.2f}s")
            print(f"   🚀 Average FPS: {fps:.1f}")
    
    def _setup_video_writer(self, output_path: str):
        """Setup video writer for saving output"""
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Video codec and settings
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 25
        frame_size = (512, 512)  # Standard avatar size
        
        return cv2.VideoWriter(output_path, fourcc, fps, frame_size)
    
    async def cleanup(self):
        """Clean up resources"""
        if self.runtime:
            await self.runtime.close()
            print("🧹 Runtime cleanup complete")

# CLI interface
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert audio file to avatar animation')
    parser.add_argument('audio_file', help='Path to input audio file')
    parser.add_argument('--output', '-o', help='Output video file path')
    parser.add_argument('--no-display', action='store_true', help='Disable real-time display')
    
    args = parser.parse_args()
    
    converter = AudioToAvatarConverter()
    
    try:
        await converter.initialize()
        await converter.process_audio_file(
            audio_file_path=args.audio_file,
            output_path=args.output,
            display_realtime=not args.no_display
        )
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await converter.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### Enhanced Version with Audio Processing

```python
# enhanced_audio_avatar.py
import asyncio
import os
import cv2
import numpy as np
import librosa
from pathlib import Path
from typing import Optional, Tuple
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk

class EnhancedAudioAvatarConverter:
    def __init__(self):
        self.runtime = None
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        
    async def initialize(self):
        """Initialize the bitHuman runtime"""
        self.runtime = await AsyncBithuman.create(
            api_secret=os.getenv('BITHUMAN_API_SECRET'),
            model_path=os.getenv('BITHUMAN_AVATAR_MODEL')
        )
        print("✅ Enhanced bitHuman runtime initialized")
    
    def validate_audio_file(self, file_path: str) -> bool:
        """Validate audio file format and existence"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        if path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {path.suffix}. Supported: {self.supported_formats}")
        
        return True
    
    def load_and_preprocess_audio(self, file_path: str, target_sr: int = 16000) -> Tuple[np.ndarray, int]:
        """Load and preprocess audio file"""
        print(f"🔊 Loading audio: {file_path}")
        
        # Load audio with librosa for better format support
        audio_data, original_sr = librosa.load(file_path, sr=None, mono=True)
        
        print(f"📊 Original: {len(audio_data)} samples at {original_sr}Hz ({len(audio_data)/original_sr:.2f}s)")
        
        # Resample if necessary
        if original_sr != target_sr:
            audio_data = librosa.resample(audio_data, orig_sr=original_sr, target_sr=target_sr)
            print(f"🔄 Resampled to {target_sr}Hz")
        
        # Normalize audio
        audio_data = self.normalize_audio(audio_data)
        
        # Convert to int16 format expected by bitHuman
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        return audio_int16, target_sr
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio to optimal levels"""
        # Remove DC offset
        audio_data = audio_data - np.mean(audio_data)
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val * 0.95  # Leave some headroom
        
        return audio_data
    
    def analyze_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> dict:
        """Analyze audio quality metrics"""
        # RMS energy
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Peak level
        peak = np.max(np.abs(audio_data))
        
        # Zero crossing rate (speech activity indicator)
        zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
        zcr = zero_crossings / len(audio_data)
        
        # Spectral centroid (brightness)
        audio_float = audio_data.astype(np.float32)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_float, sr=sample_rate)[0]
        avg_brightness = np.mean(spectral_centroid)
        
        return {
            'rms_energy': float(rms),
            'peak_level': float(peak),
            'zero_crossing_rate': float(zcr),
            'spectral_centroid': float(avg_brightness),
            'duration_seconds': len(audio_data) / sample_rate,
            'quality_score': self.calculate_quality_score(rms, peak, zcr)
        }
    
    def calculate_quality_score(self, rms: float, peak: float, zcr: float) -> float:
        """Calculate overall audio quality score (0-10)"""
        # Optimal ranges for speech
        rms_score = min(10, rms * 100)  # Higher RMS = better
        peak_score = 10 if 0.3 <= peak <= 0.95 else 5  # Good dynamic range
        zcr_score = 10 if 0.05 <= zcr <= 0.15 else 5  # Speech-like activity
        
        return (rms_score + peak_score + zcr_score) / 3
    
    async def process_with_quality_analysis(self, 
                                          audio_file_path: str, 
                                          output_path: Optional[str] = None,
                                          quality_settings: Optional[dict] = None):
        """Process audio with quality analysis and optimization"""
        
        # Validate input
        self.validate_audio_file(audio_file_path)
        
        # Load and preprocess audio
        audio_data, sample_rate = self.load_and_preprocess_audio(audio_file_path)
        
        # Analyze audio quality
        quality_metrics = self.analyze_audio_quality(audio_data, sample_rate)
        print(f"🔍 Audio Quality Analysis:")
        for key, value in quality_metrics.items():
            print(f"   {key}: {value:.3f}")
        
        # Apply quality optimizations
        if quality_settings:
            audio_data = self.apply_quality_optimizations(audio_data, quality_settings)
        
        # Create AudioChunk
        audio_chunk = AudioChunk.from_numpy(audio_data, sample_rate)
        
        # Setup video recording with metadata
        video_writer = None
        if output_path:
            video_writer = self.setup_enhanced_video_writer(output_path, quality_metrics)
        
        # Process with enhanced visualization
        await self.process_with_enhanced_display(audio_chunk, video_writer, quality_metrics)
        
        if video_writer:
            video_writer.release()
            print(f"💾 Enhanced video saved: {output_path}")
    
    def apply_quality_optimizations(self, audio_data: np.ndarray, settings: dict) -> np.ndarray:
        """Apply audio quality optimizations"""
        
        # Noise reduction
        if settings.get('noise_reduction', False):
            audio_data = self.reduce_noise(audio_data)
        
        # Dynamic range compression
        if settings.get('compression', False):
            audio_data = self.apply_compression(audio_data)
        
        # EQ adjustments
        if 'eq_boost_freq' in settings:
            audio_data = self.apply_eq(audio_data, settings['eq_boost_freq'])
        
        return audio_data
    
    def reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Simple noise reduction"""
        # Basic noise gate - remove very quiet sections
        threshold = np.mean(np.abs(audio_data)) * 0.1
        mask = np.abs(audio_data) > threshold
        audio_data[~mask] *= 0.1  # Reduce noise to 10%
        return audio_data
    
    def apply_compression(self, audio_data: np.ndarray, ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression"""
        threshold = 0.5
        above_threshold = np.abs(audio_data) > threshold
        
        # Compress audio above threshold
        compressed = np.sign(audio_data) * (
            threshold + (np.abs(audio_data) - threshold) / ratio
        )
        
        audio_data[above_threshold] = compressed[above_threshold]
        return audio_data
    
    def apply_eq(self, audio_data: np.ndarray, boost_freq: float) -> np.ndarray:
        """Apply simple EQ boost at specified frequency"""
        # This is a simplified implementation
        # In production, use proper audio processing libraries
        return audio_data
    
    def setup_enhanced_video_writer(self, output_path: str, quality_metrics: dict):
        """Setup video writer with enhanced settings"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Choose codec based on quality
        if quality_metrics['quality_score'] > 7:
            fourcc = cv2.VideoWriter_fourcc(*'H264')  # Higher quality
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Standard quality
        
        return cv2.VideoWriter(output_path, fourcc, 25, (512, 512))
    
    async def process_with_enhanced_display(self, 
                                          audio_chunk: AudioChunk, 
                                          video_writer, 
                                          quality_metrics: dict):
        """Process with enhanced real-time display"""
        
        # Setup display
        cv2.namedWindow('bitHuman Avatar - Enhanced', cv2.WINDOW_AUTOSIZE)
        
        # Create info overlay
        info_overlay = self.create_info_overlay(quality_metrics)
        
        frame_count = 0
        start_time = asyncio.get_event_loop().time()
        
        try:
            async for video_frame in self.runtime.process_audio_chunk(audio_chunk):
                # Add info overlay to frame
                enhanced_frame = self.add_overlay_to_frame(video_frame.image, info_overlay, frame_count)
                
                # Display
                cv2.imshow('bitHuman Avatar - Enhanced', enhanced_frame)
                
                # Save to video
                if video_writer:
                    video_writer.write(enhanced_frame)
                
                frame_count += 1
                
                # Update progress in window title
                if frame_count % 25 == 0:
                    progress = (frame_count / 25.0) / audio_chunk.duration * 100
                    cv2.setWindowTitle('bitHuman Avatar - Enhanced', f'Progress: {progress:.1f}%')
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            cv2.destroyAllWindows()
            
            total_time = asyncio.get_event_loop().time() - start_time
            print(f"✅ Enhanced processing complete: {frame_count} frames in {total_time:.2f}s")
    
    def create_info_overlay(self, quality_metrics: dict) -> np.ndarray:
        """Create information overlay for display"""
        overlay = np.zeros((100, 512, 3), dtype=np.uint8)
        
        # Add quality score
        quality_text = f"Quality: {quality_metrics['quality_score']:.1f}/10"
        cv2.putText(overlay, quality_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Add duration
        duration_text = f"Duration: {quality_metrics['duration_seconds']:.1f}s"
        cv2.putText(overlay, duration_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return overlay
    
    def add_overlay_to_frame(self, frame: np.ndarray, overlay: np.ndarray, frame_count: int) -> np.ndarray:
        """Add information overlay to video frame"""
        # Resize frame if needed
        if frame.shape[:2] != (512, 512):
            frame = cv2.resize(frame, (512, 512))
        
        # Add frame counter
        frame_text = f"Frame: {frame_count}"
        cv2.putText(frame, frame_text, (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Combine with overlay (you can make this more sophisticated)
        enhanced_frame = np.vstack([overlay, frame])
        
        return enhanced_frame
    
    async def cleanup(self):
        """Clean up resources"""
        if self.runtime:
            await self.runtime.close()

# Example usage with different quality settings
async def main():
    converter = EnhancedAudioAvatarConverter()
    
    try:
        await converter.initialize()
        
        # Quality optimization settings
        quality_settings = {
            'noise_reduction': True,
            'compression': True,
            'eq_boost_freq': 2000  # Boost speech frequencies
        }
        
        await converter.process_with_quality_analysis(
            audio_file_path='sample_audio.wav',
            output_path='enhanced_avatar_output.mp4',
            quality_settings=quality_settings
        )
        
    finally:
        await converter.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Batch Processing

### Batch Audio Converter

```python
# batch_converter.py
import asyncio
import os
from pathlib import Path
from typing import List
import concurrent.futures
from enhanced_audio_avatar import EnhancedAudioAvatarConverter

class BatchAudioConverter:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.converters = []
        
    async def initialize_converters(self):
        """Initialize multiple converter instances"""
        for i in range(self.max_concurrent):
            converter = EnhancedAudioAvatarConverter()
            await converter.initialize()
            self.converters.append(converter)
            print(f"✅ Converter {i+1} initialized")
    
    async def process_directory(self, 
                              input_dir: str, 
                              output_dir: str,
                              file_pattern: str = "*.wav"):
        """Process all audio files in a directory"""
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all audio files
        audio_files = list(input_path.glob(file_pattern))
        audio_files.extend(input_path.glob("*.mp3"))
        audio_files.extend(input_path.glob("*.m4a"))
        
        print(f"📁 Found {len(audio_files)} audio files to process")
        
        # Process files with limited concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_single_file(file_path):
            async with semaphore:
                converter = self.converters[len(asyncio.current_task().get_name()) % self.max_concurrent]
                
                output_file = output_path / f"{file_path.stem}_avatar.mp4"
                
                try:
                    print(f"🎬 Processing: {file_path.name}")
                    await converter.process_with_quality_analysis(
                        str(file_path),
                        str(output_file)
                    )
                    return True, file_path.name
                except Exception as e:
                    print(f"❌ Error processing {file_path.name}: {e}")
                    return False, file_path.name
        
        # Process all files
        tasks = [process_single_file(file_path) for file_path in audio_files]
        results = await asyncio.gather(*tasks)
        
        # Summary
        successful = sum(1 for success, _ in results if success)
        failed = len(results) - successful
        
        print(f"\n📊 Batch processing complete:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📁 Output directory: {output_dir}")
    
    async def cleanup(self):
        """Clean up all converters"""
        for converter in self.converters:
            await converter.cleanup()

# CLI for batch processing
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch convert audio files to avatar animations')
    parser.add_argument('input_dir', help='Input directory containing audio files')
    parser.add_argument('output_dir', help='Output directory for video files')
    parser.add_argument('--concurrent', '-c', type=int, default=3, help='Max concurrent processes')
    parser.add_argument('--pattern', '-p', default='*.wav', help='File pattern to match')
    
    args = parser.parse_args()
    
    batch_converter = BatchAudioConverter(max_concurrent=args.concurrent)
    
    try:
        await batch_converter.initialize_converters()
        await batch_converter.process_directory(
            args.input_dir,
            args.output_dir,
            args.pattern
        )
    finally:
        await batch_converter.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Features

### Real-time Audio Effects

```python
# realtime_effects.py
import asyncio
import numpy as np
from bithuman.runtime import AsyncBithuman
from bithuman.audio import AudioChunk

class AudioEffectsProcessor:
    def __init__(self):
        self.runtime = None
        self.effects_chain = []
    
    def add_effect(self, effect_func):
        """Add an audio effect to the processing chain"""
        self.effects_chain.append(effect_func)
    
    def apply_effects(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply all effects in the chain"""
        processed_audio = audio_data.copy()
        
        for effect in self.effects_chain:
            processed_audio = effect(processed_audio)
        
        return processed_audio
    
    async def process_with_effects(self, audio_chunk: AudioChunk):
        """Process audio chunk with effects"""
        # Apply effects to audio data
        processed_data = self.apply_effects(audio_chunk.data)
        
        # Create new AudioChunk with processed data
        processed_chunk = AudioChunk.from_numpy(processed_data, audio_chunk.sample_rate)
        
        # Process through bitHuman
        async for video_frame in self.runtime.process_audio_chunk(processed_chunk):
            yield video_frame

# Audio effect functions
def echo_effect(audio_data: np.ndarray, delay_samples: int = 8000, decay: float = 0.3) -> np.ndarray:
    """Add echo effect"""
    if len(audio_data) <= delay_samples:
        return audio_data
    
    echo_audio = audio_data.copy()
    echo_audio[delay_samples:] += audio_data[:-delay_samples] * decay
    
    return echo_audio

def pitch_shift(audio_data: np.ndarray, shift_factor: float = 1.1) -> np.ndarray:
    """Simple pitch shift (time-domain)"""
    # This is a simplified implementation
    # For production, use proper pitch shifting algorithms
    if shift_factor == 1.0:
        return audio_data
    
    new_length = int(len(audio_data) / shift_factor)
    indices = np.linspace(0, len(audio_data) - 1, new_length)
    
    return np.interp(indices, np.arange(len(audio_data)), audio_data)

def volume_boost(audio_data: np.ndarray, boost_db: float = 6.0) -> np.ndarray:
    """Boost volume by specified dB"""
    boost_factor = 10 ** (boost_db / 20)
    boosted = audio_data * boost_factor
    
    # Prevent clipping
    max_val = np.max(np.abs(boosted))
    if max_val > 1.0:
        boosted = boosted / max_val * 0.95
    
    return boosted

# Example usage
async def main():
    processor = AudioEffectsProcessor()
    await processor.runtime.initialize()
    
    # Add effects
    processor.add_effect(lambda x: volume_boost(x, 3.0))  # +3dB boost
    processor.add_effect(lambda x: echo_effect(x, 4000, 0.2))  # Short echo
    
    # Process audio file with effects
    audio_chunk = AudioChunk.from_file('input.wav')
    
    async for frame in processor.process_with_effects(audio_chunk):
        # Display or save frame
        pass
```

## Performance Monitoring

### Processing Analytics

```python
# processing_analytics.py
import time
import asyncio
from dataclasses import dataclass
from typing import List, Dict
import psutil

@dataclass
class ProcessingMetrics:
    file_name: str
    file_size_mb: float
    audio_duration_s: float
    processing_time_s: float
    frames_generated: int
    avg_fps: float
    peak_memory_mb: float
    cpu_usage_percent: float

class PerformanceMonitor:
    def __init__(self):
        self.metrics: List[ProcessingMetrics] = []
        self.process = psutil.Process()
    
    async def monitor_processing(self, file_path: str, processing_func):
        """Monitor processing performance"""
        # Initial measurements
        start_time = time.time()
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
        
        # Monitor during processing
        peak_memory = initial_memory
        cpu_samples = []
        frame_count = 0
        
        async def cpu_monitor():
            while True:
                cpu_percent = self.process.cpu_percent()
                cpu_samples.append(cpu_percent)
                
                current_memory = self.process.memory_info().rss / 1024 / 1024
                nonlocal peak_memory
                peak_memory = max(peak_memory, current_memory)
                
                await asyncio.sleep(0.5)
        
        # Start monitoring
        monitor_task = asyncio.create_task(cpu_monitor())
        
        try:
            # Run processing function
            result = await processing_func(file_path)
            frame_count = result.get('frame_count', 0)
            audio_duration = result.get('duration', 0)
            
        finally:
            monitor_task.cancel()
        
        # Calculate metrics
        processing_time = time.time() - start_time
        avg_fps = frame_count / processing_time if processing_time > 0 else 0
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        
        # Store metrics
        metrics = ProcessingMetrics(
            file_name=os.path.basename(file_path),
            file_size_mb=file_size,
            audio_duration_s=audio_duration,
            processing_time_s=processing_time,
            frames_generated=frame_count,
            avg_fps=avg_fps,
            peak_memory_mb=peak_memory,
            cpu_usage_percent=avg_cpu
        )
        
        self.metrics.append(metrics)
        return metrics
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        if not self.metrics:
            return {}
        
        return {
            'total_files_processed': len(self.metrics),
            'total_processing_time': sum(m.processing_time_s for m in self.metrics),
            'avg_fps': sum(m.avg_fps for m in self.metrics) / len(self.metrics),
            'avg_cpu_usage': sum(m.cpu_usage_percent for m in self.metrics) / len(self.metrics),
            'peak_memory_usage': max(m.peak_memory_mb for m in self.metrics),
            'total_frames_generated': sum(m.frames_generated for m in self.metrics)
        }
    
    def export_metrics(self, filename: str):
        """Export metrics to CSV"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'file_name', 'file_size_mb', 'audio_duration_s', 
                'processing_time_s', 'frames_generated', 'avg_fps',
                'peak_memory_mb', 'cpu_usage_percent'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for metric in self.metrics:
                writer.writerow(metric.__dict__)
        
        print(f"📊 Metrics exported to: {filename}")
```

## Common Issues and Solutions

### Memory Management

```python
# memory_manager.py
import gc
import psutil
from typing import Optional

class MemoryManager:
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process()
    
    def check_memory_usage(self) -> float:
        """Check current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def should_cleanup(self) -> bool:
        """Check if memory cleanup is needed"""
        current_memory = self.check_memory_usage()
        return current_memory > self.max_memory_mb
    
    def cleanup_memory(self):
        """Force garbage collection"""
        gc.collect()
        print(f"🧹 Memory cleanup performed. Current usage: {self.check_memory_usage():.1f}MB")
    
    async def process_with_memory_management(self, converter, file_path: str, output_path: str):
        """Process file with automatic memory management"""
        try:
            # Check memory before processing
            if self.should_cleanup():
                self.cleanup_memory()
            
            # Process file
            await converter.process_audio_file(file_path, output_path, display_realtime=False)
            
            # Cleanup after processing
            self.cleanup_memory()
            
        except MemoryError:
            print("❌ Out of memory! Try processing smaller files or reducing quality.")
            self.cleanup_memory()
            raise
```

### Error Recovery

```python
# error_recovery.py
import asyncio
import logging
from pathlib import Path

class RobustProcessor:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    async def process_with_retry(self, converter, file_path: str, output_path: str):
        """Process file with automatic retry on failure"""
        
        for attempt in range(self.max_retries + 1):
            try:
                await converter.process_audio_file(file_path, output_path)
                return True
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {file_path}: {e}")
                
                if attempt < self.max_retries:
                    # Wait before retry with exponential backoff
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    
                    # Try to recover
                    await self.attempt_recovery(converter)
                else:
                    self.logger.error(f"All attempts failed for {file_path}")
                    return False
        
        return False
    
    async def attempt_recovery(self, converter):
        """Attempt to recover from errors"""
        try:
            # Cleanup and reinitialize
            await converter.cleanup()
            await converter.initialize()
            
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
```

## Usage Examples

### Command Line Usage

```bash
# Basic usage
python audio_to_avatar.py input.wav --output output.mp4

# Batch processing
python batch_converter.py ./audio_files ./output_videos --concurrent 2

# Enhanced processing with quality analysis
python enhanced_audio_avatar.py sample.wav --output enhanced.mp4 --quality-analysis
```

### Python Script Usage

```python
# Quick single file processing
async def quick_example():
    converter = AudioToAvatarConverter()
    await converter.initialize()
    await converter.process_audio_file('speech.wav', 'avatar_speech.mp4')
    await converter.cleanup()

# Batch processing with custom settings
async def batch_example():
    batch_converter = BatchAudioConverter(max_concurrent=2)
    await batch_converter.initialize_converters()
    await batch_converter.process_directory('./audio', './videos')
    await batch_converter.cleanup()

# Run examples
asyncio.run(quick_example())
```

## Next Steps

After mastering voice-driven avatars from audio clips:

1. **[Real-time Microphone Avatar](realtime-microphone.md)** - Process live audio input
2. **[LiveKit Integration](livekit-agent.md)** - Add real-time communication features
3. **[Deploy to Production](../build/self-hosted.md)** - Scale your avatar applications

## Resources

- **[Audio Processing Guide](../generate-agent/voice-guidelines.md)** - Optimize audio input quality
- **[Performance Optimization](../build/gpu-cloud.md)** - Use GPU cloud for faster processing
- **[Community Examples](https://console.bithuman.io/#community)** - More audio-to-avatar examples

This example provides a solid foundation for creating animated avatars from audio files. Experiment with different audio formats, quality settings, and effects to achieve the best results for your use case! 