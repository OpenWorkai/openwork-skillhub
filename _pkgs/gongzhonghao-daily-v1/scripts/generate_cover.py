from PIL import Image, ImageDraw, ImageFont
import sys

# Template path
TEMPLATE_PATH = "/Users/myking/Workbuddy/Claw/cover_template.jpg"
OUTPUT_PATH = "/tmp/cover_day2.png"

# Load template
img = Image.open(TEMPLATE_PATH).convert("RGB")
draw = ImageDraw.Draw(img)
width, height = img.size

# Background color sampled from the template
# Use a horizontal gradient over the title area to match the template's subtle gradient
left_color = (243, 235, 233)
right_color = (240, 234, 237)

# Title/subtitle area (fill with horizontal gradient)
# Erase from x=110 to x=1000, y=190 to y=450
x_start, x_end = 110, 1000
y_start, y_end = 180, 450
for x in range(x_start, x_end + 1):
    t = (x - x_start) / (x_end - x_start)
    r = int(left_color[0] + (right_color[0] - left_color[0]) * t)
    g = int(left_color[1] + (right_color[1] - left_color[1]) * t)
    b = int(left_color[2] + (right_color[2] - left_color[2]) * t)
    draw.rectangle([x, y_start, x + 1, y_end], fill=(r, g, b))

# Font setup (PingFang SC)
try:
    font_path = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc"
    font_title = ImageFont.truetype(font_path, 118, index=4)
    font_subtitle = ImageFont.truetype(font_path, 58, index=4)
except Exception as e:
    print(f"Font load failed: {e}")
    sys.exit(1)

# Title and subtitle colors (matching GPT style)
title_color = (30, 40, 60)  # dark blue-gray
subtitle_color = (100, 100, 100)  # medium gray

# Draw text (scaled to 1920x814 template)
title = "大模型是个啥？"
subtitle = "用一个比喻讲清楚"

draw.text((128, 210), title, fill=title_color, font=font_title)
draw.text((128, 370), subtitle, fill=subtitle_color, font=font_subtitle)

# Save
img.save(OUTPUT_PATH)
print(f"Saved to {OUTPUT_PATH}")
