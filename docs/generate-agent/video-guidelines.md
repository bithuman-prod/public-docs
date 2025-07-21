# Video Guidelines

Video characteristics define how your bitHuman agent moves, expresses emotions, and interacts visually. This guide covers animation principles, behavioral patterns, and optimization for different use cases.

## Overview

bitHuman agents generate real-time video at 25 FPS with:
- **Facial animations** synchronized to audio
- **Expression mapping** based on content and emotion
- **Natural movements** including head gestures and eye contact
- **Consistent personality** reflected in visual behavior

## Animation Principles

### Facial Animation Fundamentals

**Lip Synchronization:**
- Automatic phoneme mapping to mouth shapes
- Natural lip movement timing
- Realistic articulation for all speech sounds
- Smooth transitions between mouth positions

**Eye Behavior:**
- Natural blink patterns (every 3-5 seconds)
- Appropriate eye contact timing
- Subtle eye movements for liveliness
- Gaze direction matching conversation flow

**Facial Expressions:**
- Emotion-appropriate expressions
- Subtle micro-expressions
- Natural expression timing
- Smooth transitions between states

### Movement Characteristics

**Head Gestures:**
```
Nodding:
- Affirmative responses
- Understanding acknowledgment
- Rhythmic agreement patterns

Head Tilts:
- Questioning or curiosity
- Thoughtful consideration
- Empathetic listening

Head Shakes:
- Negative responses
- Disagreement or correction
- Emphasis patterns
```

**Micro-Movements:**
- Subtle breathing simulation
- Natural posture adjustments
- Slight weight shifts
- Realistic idle animations

## Personality-Based Animation

### Professional/Business Agents

**Movement Characteristics:**
- Controlled, purposeful gestures
- Minimal head movement
- Professional posture maintenance
- Confident eye contact patterns

**Expression Patterns:**
- Neutral baseline with slight positive bias
- Measured emotional responses
- Professional smile timing
- Focused, attentive expressions

**Example Behaviors:**
```
Explaining concepts:
- Slight forward lean
- Occasional confirming nods
- Direct eye contact
- Minimal gestural movement

Listening mode:
- Attentive posture
- Subtle nods of understanding
- Engaged eye contact
- Neutral, focused expression
```

### Friendly/Casual Agents

**Movement Characteristics:**
- More expressive head movements
- Natural gesture patterns
- Relaxed posture
- Varied eye contact timing

**Expression Patterns:**
- Warm baseline expression
- More dynamic emotional range
- Natural smile frequency
- Expressive eyebrow movements

**Example Behaviors:**
```
Encouraging responses:
- Bright, engaging expressions
- Positive head nods
- Warm eye contact
- Slight forward lean

Conversational mode:
- Natural head tilts
- Varied facial expressions
- Dynamic eye movements
- Relaxed, open posture
```

### Energetic/Enthusiastic Agents

**Movement Characteristics:**
- Dynamic head movements
- Expressive gestures
- Animated posture changes
- High-energy eye contact

**Expression Patterns:**
- Bright, positive baseline
- Wide emotional range
- Frequent genuine smiles
- Animated eyebrow expressions

**Example Behaviors:**
```
Motivational moments:
- Energetic head movements
- Bright, encouraging smiles
- Dynamic eye contact
- Forward-leaning posture

Celebratory responses:
- Animated facial expressions
- Positive head gestures
- Bright, excited eyes
- Open, welcoming posture
```

### Calm/Soothing Agents

**Movement Characteristics:**
- Gentle, flowing movements
- Minimal head gestures
- Stable, calm posture
- Soft eye contact patterns

**Expression Patterns:**
- Peaceful baseline expression
- Subtle emotional responses
- Gentle, comforting smiles
- Soft, understanding eyes

**Example Behaviors:**
```
Comforting responses:
- Gentle, understanding nods
- Soft, empathetic expressions
- Warm, steady eye contact
- Calm, stable posture

Instructional mode:
- Patient, gentle movements
- Clear, measured expressions
- Encouraging subtle smiles
- Attentive, caring gaze
```

## Emotional Expression Guidelines

### Expression Intensity Levels

**Subtle (Level 1):**
- Micro-expressions
- Slight eyebrow movements
- Minimal mouth changes
- Soft eye adjustments

**Moderate (Level 2):**
- Clear facial expressions
- Noticeable eyebrow changes
- Visible mouth movements
- Engaged eye contact

**Strong (Level 3):**
- Full facial expressions
- Dynamic eyebrow movements
- Pronounced mouth shapes
- Intense eye engagement

### Emotion Mapping

**Positive Emotions:**
```
Happiness/Joy:
- Genuine smile activation
- Bright, engaged eyes
- Slight head lift
- Open, welcoming expression

Excitement/Enthusiasm:
- Wide eyes
- Broad smile
- Dynamic head movements
- Animated facial features

Satisfaction/Pride:
- Confident smile
- Direct eye contact
- Slight chin lift
- Composed, pleased expression
```

**Neutral Emotions:**
```
Thoughtfulness:
- Slight frown of concentration
- Tilted head position
- Focused eyes
- Pursed or neutral lips

Curiosity:
- Raised eyebrows
- Head tilt
- Bright, questioning eyes
- Slightly open mouth

Professional Focus:
- Neutral, attentive expression
- Direct eye contact
- Composed mouth
- Alert, engaged posture
```

**Supportive Emotions:**
```
Empathy/Understanding:
- Soft, caring eyes
- Gentle expression
- Slight head tilt
- Warm, supportive smile

Encouragement:
- Positive, affirming nods
- Bright, supportive eyes
- Encouraging smile
- Forward-leaning posture

Patience:
- Calm, steady expression
- Gentle eye contact
- Neutral, accepting mouth
- Relaxed, stable posture
```

## Technical Considerations

### Frame Rate and Timing

**25 FPS Standard:**
- Smooth, natural-looking animation
- Synchronized with audio processing
- Optimized for real-time generation
- Compatible with streaming platforms

**Animation Timing:**
```
Blink Duration: 150-200ms (4-5 frames)
Expression Change: 500-1000ms (12-25 frames)
Head Movement: 1-2 seconds (25-50 frames)
Gesture Cycle: 2-4 seconds (50-100 frames)
```

### Visual Quality Optimization

**Resolution Considerations:**
- Standard: 512x512 pixels
- High Quality: 1024x1024 pixels
- Professional: 1920x1080 pixels
- Performance vs. quality trade-offs

**Compression Settings:**
```
Real-time Streaming:
- H.264 codec
- Variable bitrate
- Low-latency settings

High-Quality Recording:
- Minimal compression
- High bitrate settings
- Professional codecs
```

## Customization Options

### Behavioral Parameters

**Animation Intensity:**
```
Conservative (0.3):
- Subtle movements
- Minimal expressions
- Professional demeanor

Moderate (0.7):
- Natural movement range
- Balanced expressions
- Conversational feel

Expressive (1.0):
- Full animation range
- Dynamic expressions
- Engaging personality
```

**Gesture Frequency:**
```
Minimal (0.2):
- Rare head movements
- Subtle gestures only
- Focused on speech

Normal (0.5):
- Natural gesture timing
- Balanced movement
- Conversational rhythm

Active (0.8):
- Frequent gestures
- Dynamic movement
- Engaging animation
```

### Expression Responsiveness

**Emotion Sensitivity:**
- How quickly expressions change
- Intensity of emotional responses
- Duration of expression holds

**Context Awareness:**
- Content-appropriate expressions
- Situation-sensitive behavior
- Personality-consistent reactions

## Use Case Optimization

### Business Presentations

**Recommended Settings:**
- Professional animation level (0.4-0.6)
- Controlled gesture frequency
- Focused eye contact patterns
- Minimal background movement

**Key Behaviors:**
- Authoritative posture
- Clear, deliberate expressions
- Professional gesture timing
- Confident eye engagement

### Educational Content

**Recommended Settings:**
- Engaging animation level (0.6-0.8)
- Natural gesture frequency
- Encouraging expressions
- Supportive body language

**Key Behaviors:**
- Patient, understanding expressions
- Encouraging nods and smiles
- Clear, explanatory gestures
- Warm, approachable demeanor

### Customer Service

**Recommended Settings:**
- Balanced animation level (0.5-0.7)
- Responsive gesture timing
- Empathetic expressions
- Professional yet warm behavior

**Key Behaviors:**
- Attentive listening posture
- Understanding acknowledgments
- Professional helpfulness
- Calm, reassuring presence

### Entertainment/Gaming

**Recommended Settings:**
- High animation level (0.8-1.0)
- Dynamic gesture frequency
- Expressive emotional range
- Engaging, lively behavior

**Key Behaviors:**
- Animated expressions
- Dynamic movement patterns
- Engaging eye contact
- Personality-driven gestures

## Performance Optimization

### Real-time Considerations

**Latency Minimization:**
- Optimize animation complexity
- Balance quality vs. speed
- Consider hardware limitations
- Stream-appropriate settings

**Resource Management:**
```
CPU Optimization:
- Efficient animation algorithms
- Selective detail rendering
- Smart caching strategies

GPU Acceleration:
- Hardware-accelerated rendering
- Parallel processing utilization
- Optimized shader usage

Memory Usage:
- Efficient texture management
- Smart asset loading
- Memory pool optimization
```

### Quality vs. Performance

**High Performance Mode:**
- Reduced animation complexity
- Lower resolution output
- Simplified expressions
- Optimized for speed

**Balanced Mode:**
- Standard animation quality
- Moderate resource usage
- Good visual fidelity
- Real-time capability

**High Quality Mode:**
- Full animation detail
- Maximum resolution
- Rich expressions
- Optimized for quality

## Testing and Validation

### Animation Quality Checklist

- [ ] **Smooth movement** - No jerky or unnatural motion
- [ ] **Sync accuracy** - Lips match audio timing
- [ ] **Expression appropriateness** - Emotions match content
- [ ] **Personality consistency** - Behavior matches character
- [ ] **Natural timing** - Realistic gesture duration
- [ ] **Eye contact quality** - Engaging and appropriate

### Performance Testing

```python
# Example performance monitoring
import time
from bithuman.runtime import AsyncBithuman

async def test_performance():
    runtime = await AsyncBithuman.create(...)
    
    frame_times = []
    async for frame in runtime.process_audio_chunk(audio):
        start_time = time.time()
        # Process frame
        frame_time = time.time() - start_time
        frame_times.append(frame_time)
    
    avg_fps = 1.0 / (sum(frame_times) / len(frame_times))
    print(f"Average FPS: {avg_fps:.2f}")
```

## Next Steps

After optimizing video characteristics:

1. **[Test Complete Agent](../getting-started/first-model.md)** - Integrate all components
2. **[Explore Integrations](../integrations/livekit.md)** - Deploy in applications
3. **[Monitor Performance](../build/self-hosted.md)** - Optimize for production
4. **Iterate** - Refine based on user feedback

## Resources

### Animation References
- **Professional presenters** - Business behavior patterns
- **TV personalities** - Engaging presentation styles
- **Educational content** - Teaching behavior examples
- **Customer service training** - Professional interaction models

### Technical Documentation
- **Animation principles** - Fundamental movement theory
- **Facial coding** - Expression classification systems
- **Performance optimization** - Real-time rendering techniques
- **User experience** - Interaction design principles

### Community Examples

Visit our [Community Hub](https://console.bithuman.io/#community) to:
- See animation examples
- Compare different styles
- Learn optimization techniques
- Share your own discoveries

Remember: Great animation brings your bitHuman agent to life and creates engaging, believable interactions! 