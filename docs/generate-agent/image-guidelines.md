# Image Guidelines

High-quality reference images are essential for creating compelling bitHuman agents. This guide covers technical requirements, composition best practices, and tips for optimal results.

## Image Requirements

### Technical Specifications

| Requirement | Specification | Notes |
|-------------|---------------|-------|
| **Resolution** | 1024x1024 minimum | Higher resolution = better quality |
| **Format** | PNG, JPG, WebP | PNG preferred for transparency |
| **Color Space** | sRGB | Ensures consistent color reproduction |
| **File Size** | Under 50MB | Larger files may timeout during processing |
| **Aspect Ratio** | 1:1 (square) preferred | Other ratios will be cropped |

### Quality Standards

- **High resolution**: Sharp, clear details
- **Good lighting**: Even, natural illumination
- **Minimal compression**: Avoid heavily compressed images
- **No watermarks**: Clean, unobstructed images

## Composition Guidelines

### Head and Shoulders Frame

```
✅ IDEAL COMPOSITION:
- Head and shoulders visible
- Face takes up 60-70% of frame height
- Clear view of facial features
- Slight head tilt adds natural feel
- Natural, relaxed expression
```

### Facial Features

**Eyes**
- Both eyes clearly visible
- Natural eye contact or slight off-camera gaze
- Avoid extreme expressions (unless intentional)
- Consider lighting on eyes for liveliness

**Mouth and Expression**
- Natural, relaxed mouth position
- Slight smile often works well
- Avoid extreme expressions for base image
- Consider what expressions suit your agent's personality

**Facial Angle**
- Front-facing or slight 3/4 angle preferred
- Avoid extreme profile views
- Consider agent's intended interaction style

### Background Considerations

```
✅ RECOMMENDED:
- Clean, neutral backgrounds
- Subtle gradients or textures
- Professional or contextually appropriate settings
- Good contrast with subject

❌ AVOID:
- Busy, distracting backgrounds
- Cluttered environments
- Competing visual elements
- Poor contrast with subject
```

## Lighting Best Practices

### Natural Lighting
- **Soft, diffused light** - Avoid harsh shadows
- **Front or side lighting** - Illuminates face evenly
- **Golden hour** - Warm, flattering light
- **Overcast conditions** - Natural light diffusion

### Studio Lighting
- **Key light** - Primary illumination at 45° angle
- **Fill light** - Reduces harsh shadows
- **Background light** - Separates subject from background
- **Hair light** - Adds dimension and depth

### Lighting Setup Examples

#### Professional Headshot Setup
```
Key Light (45° left) + Fill Light (30° right) + Background Light
= Even, professional illumination with minimal shadows
```

#### Natural Light Setup
```
Large window + White reflector opposite
= Soft, natural-looking illumination
```

## Style Guidelines

### Professional Agents

**Characteristics:**
- Clean, polished appearance
- Professional attire
- Confident posture
- Neutral to slight smile
- Good eye contact

**Examples:**
- Business consultants
- Financial advisors
- Legal professionals
- Medical practitioners

### Casual/Friendly Agents

**Characteristics:**
- Relaxed, approachable appearance
- Casual but neat attire
- Warm expression
- Natural smile
- Engaging eye contact

**Examples:**
- Teachers
- Coaches
- Customer service
- Community helpers

### Creative/Artistic Agents

**Characteristics:**
- Expressive appearance
- Unique style choices
- Dynamic expressions
- Creative backgrounds
- Personality-driven composition

**Examples:**
- Artists
- Musicians
- Designers
- Content creators

## Age and Demographics

### Age Considerations

**Young Adults (20-30)**
- Fresh, energetic appearance
- Contemporary styling
- Bright, clear eyes
- Modern backgrounds

**Middle-aged (30-50)**
- Professional, experienced look
- Sophisticated styling
- Confident expressions
- Polished backgrounds

**Mature Adults (50+)**
- Distinguished appearance
- Classic styling
- Wise, approachable expressions
- Elegant backgrounds

### Diversity and Inclusion

- **Represent diverse ethnicities**
- **Include various ages**
- **Consider different cultural backgrounds**
- **Ensure inclusive representation**
- **Avoid stereotypes**

## Common Issues and Solutions

### Problem: Poor Image Quality

**Symptoms:**
- Blurry or pixelated results
- Loss of facial details
- Inconsistent rendering

**Solutions:**
- Use higher resolution source images
- Ensure sharp focus on facial features
- Avoid heavily compressed images
- Check lighting quality

### Problem: Inconsistent Expressions

**Symptoms:**
- Unnatural facial movements
- Expression doesn't match personality
- Limited range of emotions

**Solutions:**
- Use neutral base expression
- Ensure clear facial feature visibility
- Consider multiple reference angles
- Test with different emotional states

### Problem: Background Interference

**Symptoms:**
- Avatar appears to merge with background
- Distracting elements in render
- Poor edge definition

**Solutions:**
- Use clean, contrasted backgrounds
- Ensure clear subject separation
- Consider background removal
- Test different background types

## Image Collection Strategy

### Single Image Approach
```
✅ Best for: Simple, consistent agents
Requirements:
- High-quality headshot
- Perfect lighting
- Ideal expression
- Professional composition
```

### Multiple Image Approach
```
✅ Best for: Dynamic, expressive agents
Requirements:
- Multiple angles (front, 3/4, profile)
- Various expressions (neutral, smile, thoughtful)
- Consistent lighting across images
- Same outfit/styling
```

## Pre-Processing Tips

### Basic Adjustments
```python
# Example image preprocessing
import cv2
import numpy as np

def preprocess_image(image_path):
    # Load image
    img = cv2.imread(image_path)
    
    # Enhance contrast
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    lab[...,0] = clahe.apply(lab[...,0])
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Slight sharpening
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    img = cv2.filter2D(img, -1, kernel)
    
    return img
```

### Professional Tools
- **Adobe Photoshop** - Professional editing
- **GIMP** - Free alternative
- **Lightroom** - Photo enhancement
- **Canva** - Simple editing tools

## Testing Your Images

### Quality Checklist

- [ ] **Resolution**: 1024x1024 or higher
- [ ] **Focus**: Sharp facial features
- [ ] **Lighting**: Even, natural illumination
- [ ] **Expression**: Appropriate for agent personality
- [ ] **Background**: Clean and non-distracting
- [ ] **Composition**: Well-framed head and shoulders
- [ ] **Quality**: Minimal compression artifacts

### A/B Testing
1. Create agent with Image A
2. Create agent with Image B
3. Test both with sample interactions
4. Compare quality and consistency
5. Choose best performing image

## Advanced Techniques

### Multi-Angle Collection
```
Front view (0°) - Base reference
3/4 left (45°) - Natural conversation angle
3/4 right (45°) - Alternative angle
Slight up angle - Dynamic variation
```

### Expression Mapping
```
Neutral - Base state
Slight smile - Positive interactions
Thoughtful - Processing information
Confident - Authoritative responses
```

### Style Consistency
- Maintain same lighting setup
- Use consistent clothing/styling
- Keep same camera distance
- Preserve color temperature

## Next Steps

After preparing your images:

1. **[Review Voice Guidelines](voice-guidelines.md)** - Align audio characteristics
2. **[Check Video Guidelines](video-guidelines.md)** - Plan animation behavior
3. **Upload and Test** - Create agent and evaluate results
4. **Iterate** - Refine based on output quality

## Resources

### Stock Photography
- **Unsplash** - High-quality free images
- **Pexels** - Professional stock photos
- **Getty Images** - Premium photography
- **Adobe Stock** - Professional content

### Photography Tools
- **Camera smartphones** - Often sufficient quality
- **DSLR cameras** - Professional results
- **Ring lights** - Consistent lighting
- **Softboxes** - Professional lighting

### Editing Software
- **Free**: GIMP, Canva, Photopea
- **Paid**: Photoshop, Lightroom, Affinity Photo
- **Mobile**: Snapseed, VSCO, Adobe Mobile

## Community Examples

Visit our [Community Hub](https://console.bithuman.io/#community) to see:
- Successful image examples
- Before/after comparisons
- Style variations
- Technical tips from other creators

Remember: Great images are the foundation of compelling bitHuman agents. Invest time in getting them right! 