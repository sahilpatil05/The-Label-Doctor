#!/usr/bin/env python3
"""
Create a simple test image with ingredient text for OCR testing
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

# Create image
width, height = 800, 600
background_color = (255, 255, 255)  # White
text_color = (0, 0, 0)  # Black

image = Image.new('RGB', (width, height), background_color)
draw = ImageDraw.Draw(image)

# Try to use a nice font, fall back to default if not available
try:
    font_large = ImageFont.truetype("arial.ttf", 28)
    font_normal = ImageFont.truetype("arial.ttf", 20)
except:
    font_large = ImageFont.load_default()
    font_normal = ImageFont.load_default()

# Add text - ingredient label
y_pos = 30

title = "INGREDIENTS:"
draw.text((40, y_pos), title, font=font_large, fill=text_color)
y_pos += 50

ingredients = [
    "Enriched unbleached flour (wheat flour, malted barley flour, ascorbic acid)",
    "Sugar, degermed yellow cornmeal, salt",
    "Leavening (baking soda, sodium acid pyrophosphate)",
    "Soybean oil, honey, natural and artificial flavor",
    "Contains: Wheat, may contain: Peanuts, Tree nuts",
    "",
    "ALLERGEN INFORMATION:",
    "Contains: Wheat, Soy",
    "Produced on shared equipment with peanuts and tree nuts"
]

for line in ingredients:
    if line:
        # Wrap text if too long
        wrapped_lines = textwrap.wrap(line, width=70)
        for wrapped_line in wrapped_lines:
            draw.text((40, y_pos), wrapped_line, font=font_normal, fill=text_color)
            y_pos += 30
    else:
        y_pos += 15

# Save image
output_file = "test_food_label.jpg"
image.save(output_file, quality=95)
print(f"✅ Created test image: {output_file}")
print(f"   Dimensions: {width}x{height}")
print(f"   File size: {Path(output_file).stat().st_size if Path(output_file).exists() else 'unknown'} bytes")
