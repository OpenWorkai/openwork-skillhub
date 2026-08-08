from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# Output directory for generated illustrations (override with OW_ILLUSTRATION_DIR)
OUT_DIR = os.environ.get(
    "OW_ILLUSTRATION_DIR",
    os.path.join(os.path.dirname(__file__), "..", "output"),
)
os.makedirs(OUT_DIR, exist_ok=True)

# Colors matching the cover template
BG_TOP = (247, 242, 245)
BG_BOTTOM = (235, 228, 237)
ACCENT_PURPLE = (123, 107, 141)
LIGHT_PURPLE = (176, 161, 195)
SOFT_LAVENDER = (210, 200, 220)
PALE_LAVENDER = (232, 226, 237)
DARK_TEXT = (45, 62, 79)
WHITE = (255, 255, 255)

def create_gradient_bg(width, height, top, bottom):
    img = Image.new('RGB', (width, height), top)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

def get_font(size):
    fonts = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for f in fonts:
        try:
            return ImageFont.truetype(f, size)
        except:
            continue
    return ImageFont.load_default()

def draw_text_centered(draw, text, center, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center[0] - w/2, center[1] - h/2), text, font=font, fill=fill)

def draw_text_left(draw, text, pos, font, fill):
    draw.text(pos, text, font=font, fill=fill)

def draw_circle(draw, center, radius, fill, outline=None, width=1):
    x, y = center
    draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=fill, outline=outline, width=width)

def draw_rounded_shadow(img, xy, radius, blur=12):
    x1, y1, x2, y2 = xy
    shadow = Image.new('RGBA', (x2-x1+blur*3, y2-y1+blur*3), (0,0,0,0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([blur, blur, x2-x1+blur*2, y2-y1+blur*2], radius=radius, fill=(140, 130, 145, 35))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    img.paste(shadow, (x1-blur, y1-blur), shadow)

# ============= IMAGE 1: Traditional vs AI =============
def create_image1():
    W, H = 1200, 800
    img = create_gradient_bg(W, H, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    
    title_font = get_font(44)
    label_font = get_font(30)
    small_font = get_font(22)
    
    # Title
    draw_text_centered(draw, "传统程序 vs AI 程序", (W//2, 70), title_font, DARK_TEXT)
    draw.line([(W//2-80, 115), (W//2+80, 115)], fill=ACCENT_PURPLE, width=4)
    
    card_w, card_h = 460, 560
    card_y = 150
    
    # Left card: Traditional program
    left_x = 90
    draw_rounded_shadow(img, [left_x, card_y, left_x+card_w, card_y+card_h], 30)
    draw.rounded_rectangle([left_x, card_y, left_x+card_w, card_y+card_h], radius=30, fill=WHITE, outline=PALE_LAVENDER, width=2)
    
    # Rule book illustration
    book_x, book_y = left_x + card_w//2, card_y + 130
    bw = 100  # book half-width
    # Book cover with shadow
    draw_rounded_shadow(img, [book_x-bw, book_y-100, book_x+bw, book_y+100], 14, blur=8)
    draw.rounded_rectangle([book_x-bw, book_y-100, book_x+bw, book_y+100], radius=14, fill=(250, 248, 252), outline=ACCENT_PURPLE, width=3)
    # Spine
    draw.line([(book_x-22, book_y-100), (book_x-22, book_y+100)], fill=ACCENT_PURPLE, width=3)
    # Title on book
    draw_text_centered(draw, "猫的特征手册", (book_x+12, book_y-72), small_font, ACCENT_PURPLE)
    # Checklist items
    items = ["尖耳朵", "四条腿", "会喵喵", "毛茸茸"]
    for i, txt in enumerate(items):
        y = book_y - 38 + i * 38
        draw.rectangle([book_x-80, y-8, book_x-60, y+12], fill=ACCENT_PURPLE, outline=None)
        # check mark
        draw.line([(book_x-78, y+2), (book_x-73, y+7), (book_x-64, y-3)], fill=WHITE, width=3)
        draw_text_left(draw, txt, (book_x-50, y-8), small_font, DARK_TEXT)
    
    # Label
    draw_text_centered(draw, "普通程序", (left_x+card_w//2, card_y+280), label_font, DARK_TEXT)
    desc = "人写好规则，程序照着执行"
    draw_text_centered(draw, desc, (left_x+card_w//2, card_y+335), small_font, ACCENT_PURPLE)
    
    # Right card: AI program
    right_x = W - 90 - card_w
    draw_rounded_shadow(img, [right_x, card_y, right_x+card_w, card_y+card_h], 30)
    draw.rounded_rectangle([right_x, card_y, right_x+card_w, card_y+card_h], radius=30, fill=WHITE, outline=PALE_LAVENDER, width=2)
    
    # Neural network at top
    node_y = card_y + 55
    nodes = [right_x+card_w//2-70, right_x+card_w//2, right_x+card_w//2+70]
    for nx in nodes:
        draw_circle(draw, (nx, node_y), 10, ACCENT_PURPLE)
    draw.line([(nodes[0], node_y), (nodes[1], node_y)], fill=ACCENT_PURPLE, width=3)
    draw.line([(nodes[1], node_y), (nodes[2], node_y)], fill=ACCENT_PURPLE, width=3)
    # connections down to photos
    draw.line([(nodes[0], node_y+10), (right_x+card_w//2-50, card_y+115)], fill=LIGHT_PURPLE, width=2)
    draw.line([(nodes[1], node_y+10), (right_x+card_w//2, card_y+115)], fill=LIGHT_PURPLE, width=2)
    draw.line([(nodes[2], node_y+10), (right_x+card_w//2+50, card_y+115)], fill=LIGHT_PURPLE, width=2)
    
    # Stack of photos
    photo_w, photo_h = 110, 90
    photos = [
        (right_x+card_w//2-55, card_y+115, (250, 248, 252)),
        (right_x+card_w//2-35, card_y+145, (245, 242, 248)),
        (right_x+card_w//2-15, card_y+175, (250, 248, 252)),
    ]
    for px, py, bg in photos:
        draw.rounded_rectangle([px, py, px+photo_w, py+photo_h], radius=12, fill=bg, outline=LIGHT_PURPLE, width=2)
    
    # Top photo: cat face
    cat_cx, cat_cy = photos[-1][0] + photo_w//2, photos[-1][1] + photo_h//2
    # head
    draw_circle(draw, (cat_cx, cat_cy+6), 32, SOFT_LAVENDER)
    # ears
    draw.polygon([(cat_cx-25, cat_cy-8), (cat_cx-12, cat_cy-32), (cat_cx-2, cat_cy-8)], fill=SOFT_LAVENDER)
    draw.polygon([(cat_cx+25, cat_cy-8), (cat_cx+12, cat_cy-32), (cat_cx+2, cat_cy-8)], fill=SOFT_LAVENDER)
    # inner ears
    draw.polygon([(cat_cx-18, cat_cy-10), (cat_cx-12, cat_cy-24), (cat_cx-8, cat_cy-10)], fill=LIGHT_PURPLE)
    draw.polygon([(cat_cx+18, cat_cy-10), (cat_cx+12, cat_cy-24), (cat_cx+8, cat_cy-10)], fill=LIGHT_PURPLE)
    # eyes
    draw_circle(draw, (cat_cx-11, cat_cy+4), 5, DARK_TEXT)
    draw_circle(draw, (cat_cx+11, cat_cy+4), 5, DARK_TEXT)
    # shine
    draw_circle(draw, (cat_cx-13, cat_cy+2), 2, WHITE)
    draw_circle(draw, (cat_cx+9, cat_cy+2), 2, WHITE)
    # nose
    draw.polygon([(cat_cx, cat_cy+12), (cat_cx-5, cat_cy+20), (cat_cx+5, cat_cy+20)], fill=ACCENT_PURPLE)
    # mouth
    draw.arc([cat_cx-8, cat_cy+18, cat_cx, cat_cy+28], start=0, end=180, fill=ACCENT_PURPLE, width=2)
    draw.arc([cat_cx, cat_cy+18, cat_cx+8, cat_cy+28], start=0, end=180, fill=ACCENT_PURPLE, width=2)
    
    # "10000+" badge
    badge_x, badge_y = right_x + card_w - 70, card_y + 260
    draw_circle(draw, (badge_x, badge_y), 38, ACCENT_PURPLE)
    draw_text_centered(draw, "10000+", (badge_x, badge_y-6), get_font(18), WHITE)
    draw_text_centered(draw, "张照片", (badge_x, badge_y+16), get_font(14), WHITE)
    
    # Label
    draw_text_centered(draw, "AI 程序", (right_x+card_w//2, card_y+290), label_font, DARK_TEXT)
    desc = "给它海量照片，它自己找规律"
    draw_text_centered(draw, desc, (right_x+card_w//2, card_y+345), small_font, ACCENT_PURPLE)
    
    # Center arrow
    arrow_x = W//2
    arrow_y = card_y + card_h//2
    draw.polygon([(arrow_x-18, arrow_y-24), (arrow_x+18, arrow_y), (arrow_x-18, arrow_y+24)], fill=ACCENT_PURPLE)
    
    return img

# ============= IMAGE 2: AI in daily life =============
def create_image2():
    W, H = 1200, 800
    img = create_gradient_bg(W, H, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    
    title_font = get_font(44)
    label_font = get_font(28)
    small_font = get_font(22)
    tiny_font = get_font(18)
    
    # Title
    draw_text_centered(draw, "其实你早就在用 AI 了", (W//2, 70), title_font, DARK_TEXT)
    draw.line([(W//2-80, 115), (W//2+80, 115)], fill=ACCENT_PURPLE, width=4)
    
    # Center phone
    phone_w, phone_h = 240, 420
    phone_x = (W - phone_w) // 2
    phone_y = 150
    draw_rounded_shadow(img, [phone_x, phone_y, phone_x+phone_w, phone_y+phone_h], 32, blur=14)
    draw.rounded_rectangle([phone_x, phone_y, phone_x+phone_w, phone_y+phone_h], radius=32, fill=WHITE, outline=ACCENT_PURPLE, width=3)
    # Screen
    draw.rounded_rectangle([phone_x+16, phone_y+16, phone_x+phone_w-16, phone_y+phone_h-16], radius=24, fill=(248, 246, 250), outline=None)
    # Notch
    draw.rounded_rectangle([phone_x+80, phone_y+10, phone_x+phone_w-80, phone_y+26], radius=8, fill=DARK_TEXT)
    
    # Chat bubbles on screen
    bubble1_y = phone_y + 70
    draw.rounded_rectangle([phone_x+38, bubble1_y, phone_x+phone_w-38, bubble1_y+55], radius=18, fill=PALE_LAVENDER)
    draw_text_centered(draw, "你好，AI", (phone_x+phone_w//2, bubble1_y+27), small_font, DARK_TEXT)
    
    bubble2_y = bubble1_y + 75
    draw.rounded_rectangle([phone_x+38, bubble2_y, phone_x+phone_w-38, bubble2_y+100], radius=18, fill=ACCENT_PURPLE)
    draw_text_centered(draw, "我在呢，", (phone_x+phone_w//2, bubble2_y+32), small_font, WHITE)
    draw_text_centered(draw, "有什么可以帮你？", (phone_x+phone_w//2, bubble2_y+65), small_font, WHITE)
    
    # Face ID at bottom of screen
    face_y = phone_y + phone_h - 100
    draw_circle(draw, (phone_x+phone_w//2, face_y), 32, PALE_LAVENDER, outline=LIGHT_PURPLE, width=2)
    # face outline
    draw.arc([phone_x+phone_w//2-18, face_y-16, phone_x+phone_w//2+18, face_y+14], start=10, end=170, fill=ACCENT_PURPLE, width=3)
    draw_circle(draw, (phone_x+phone_w//2-8, face_y-4), 3, ACCENT_PURPLE)
    draw_circle(draw, (phone_x+phone_w//2+8, face_y-4), 3, ACCENT_PURPLE)
    draw.polygon([(phone_x+phone_w//2, face_y+4), (phone_x+phone_w//2-4, face_y+10), (phone_x+phone_w//2+4, face_y+10)], fill=ACCENT_PURPLE)
    
    # Floating cards around phone
    cards = [
        (70, 180, "Face ID", "face"),
        (70, 420, "猜你喜欢", "shop"),
        (W-70-230, 180, "联想词", "keyboard"),
        (W-70-230, 420, "AI 助手", "chat"),
    ]
    
    for cx, cy, title, icon_type in cards:
        card_w, card_h = 230, 150
        # Draw connecting line
        if cx < W//2:
            line_start = (cx+card_w-10, cy+card_h//2)
            line_end = (phone_x+10, phone_y + phone_h//2)
        else:
            line_start = (cx+10, cy+card_h//2)
            line_end = (phone_x+phone_w-10, phone_y + phone_h//2)
        draw.line([line_start, line_end], fill=LIGHT_PURPLE, width=2)
        
        draw_rounded_shadow(img, [cx, cy, cx+card_w, cy+card_h], 24, blur=10)
        draw.rounded_rectangle([cx, cy, cx+card_w, cy+card_h], radius=24, fill=WHITE, outline=PALE_LAVENDER, width=2)
        
        # Icon background
        icon_cx, icon_cy = cx + card_w//2, cy + 55
        draw_circle(draw, (icon_cx, icon_cy), 36, (245, 242, 248))
        
        if icon_type == "face":
            # face icon
            draw_circle(draw, (icon_cx, icon_cy), 22, PALE_LAVENDER, outline=ACCENT_PURPLE, width=2)
            draw.arc([icon_cx-14, icon_cy-10, icon_cx+14, icon_cy+12], start=10, end=170, fill=ACCENT_PURPLE, width=2)
            draw_circle(draw, (icon_cx-6, icon_cy-3), 3, ACCENT_PURPLE)
            draw_circle(draw, (icon_cx+6, icon_cy-3), 3, ACCENT_PURPLE)
            draw.polygon([(icon_cx, icon_cy+5), (icon_cx-3, icon_cy+11), (icon_cx+3, icon_cy+11)], fill=ACCENT_PURPLE)
            # scanning lines
            draw.line([(icon_cx-22, icon_cy-14), (icon_cx-14, icon_cy-14)], fill=ACCENT_PURPLE, width=2)
            draw.line([(icon_cx+14, icon_cy-14), (icon_cx+22, icon_cy-14)], fill=ACCENT_PURPLE, width=2)
            
        elif icon_type == "shop":
            # heart
            heart_x, heart_y = icon_cx + 16, icon_cy - 18
            draw.polygon([(heart_x, heart_y), (heart_x+6, heart_y-6), (heart_x+12, heart_y), (heart_x+6, heart_y+8)], fill=ACCENT_PURPLE)
            # shopping cart
            cart_y = icon_cy + 6
            draw.arc([icon_cx-20, cart_y-12, icon_cx+6, cart_y+12], start=180, end=360, fill=ACCENT_PURPLE, width=3)
            draw.line([(icon_cx-20, cart_y), (icon_cx-24, cart_y+18)], fill=ACCENT_PURPLE, width=3)
            draw.line([(icon_cx+6, cart_y), (icon_cx+10, cart_y+18)], fill=ACCENT_PURPLE, width=3)
            draw.line([(icon_cx-24, cart_y+18), (icon_cx+10, cart_y+18)], fill=ACCENT_PURPLE, width=3)
            draw_circle(draw, (icon_cx-12, cart_y+26), 4, ACCENT_PURPLE)
            draw_circle(draw, (icon_cx+2, cart_y+26), 4, ACCENT_PURPLE)
            
        elif icon_type == "keyboard":
            # keyboard
            draw.rounded_rectangle([icon_cx-24, icon_cy-10, icon_cx+24, icon_cy+10], radius=4, fill=PALE_LAVENDER, outline=ACCENT_PURPLE, width=2)
            keys = [(-18, -4), (-6, -4), (6, -4), (18, -4), (-12, 4), (0, 4), (12, 4)]
            for kx, ky in keys:
                draw.rectangle([icon_cx+kx-4, icon_cy+ky-3, icon_cx+kx+4, icon_cy+ky+3], fill=ACCENT_PURPLE)
            # suggestion bubble
            draw.rounded_rectangle([icon_cx+14, icon_cy-26, icon_cx+34, icon_cy-8], radius=6, fill=SOFT_LAVENDER)
            draw_text_centered(draw, "AI", (icon_cx+24, icon_cy-17), tiny_font, WHITE)
            
        elif icon_type == "chat":
            # chat bubble
            draw.rounded_rectangle([icon_cx-18, icon_cy-16, icon_cx+18, icon_cy+6], radius=10, fill=SOFT_LAVENDER)
            draw.polygon([(icon_cx-8, icon_cy+6), (icon_cx-2, icon_cy+16), (icon_cx+4, icon_cy+6)], fill=SOFT_LAVENDER)
            draw_text_centered(draw, "AI", (icon_cx, icon_cy-5), small_font, WHITE)
            # sparkle
            draw.polygon([(icon_cx+22, icon_cy-12), (icon_cx+24, icon_cy-18), (icon_cx+26, icon_cy-12), (icon_cx+32, icon_cy-10), (icon_cx+26, icon_cy-8), (icon_cx+24, icon_cy-2), (icon_cx+22, icon_cy-8), (icon_cx+16, icon_cy-10)], fill=ACCENT_PURPLE)
        
        # Label
        draw_text_centered(draw, title, (cx+card_w//2, cy+115), label_font, DARK_TEXT)
    
    return img

if __name__ == "__main__":
    img1 = create_image1()
    img1.save(os.path.join(OUT_DIR, "day1_illustration_01.png"), quality=95)
    print(f"Saved {os.path.join(OUT_DIR, 'day1_illustration_01.png')}")
    
    img2 = create_image2()
    img2.save(os.path.join(OUT_DIR, "day1_illustration_02.png"), quality=95)
    print(f"Saved {os.path.join(OUT_DIR, 'day1_illustration_02.png')}")
