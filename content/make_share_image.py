"""Draws img/share.jpg, the 1200x630 image shown in WhatsApp / Facebook / Google link previews.
Run from the project folder:  python content/make_share_image.py
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
GREEN_900 = (18, 64, 34)
GREEN_700 = (30, 107, 47)
GOLD = (214, 166, 83)
CREAM = (250, 246, 236)
CREAM_GOLD = (243, 227, 181)
F = 'C:/Windows/Fonts/'

img = Image.new('RGB', (W, H), GREEN_900)

# soft light glow behind the text
glow = Image.new('L', (W, H), 0)
ImageDraw.Draw(glow).ellipse((-200, -260, 760, 520), fill=90)
glow = glow.filter(ImageFilter.GaussianBlur(120))
img.paste(Image.new('RGB', (W, H), GREEN_700), (0, 0), glow)

# faint gold eight-point-star pattern
pat = Image.new('RGBA', (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(pat)
step = 90
for gx in range(-step, W + step, step):
    for gy in range(-step, H + step, step):
        cx, cy, r = gx + step / 2, gy + step / 2, 26
        sq1 = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
        sq2 = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (0, 90, 180, 270)]
        pd.polygon(sq1, outline=GOLD + (38,), width=2)
        pd.polygon(sq2, outline=GOLD + (38,), width=2)
img.paste(pat, (0, 0), pat)

d = ImageDraw.Draw(img)

# gold frame
d.rectangle((18, 18, W - 19, H - 19), outline=GOLD, width=3)

# arched portrait on the right
pw, ph = 330, 450
px, py = W - pw - 80, (H - ph) // 2 + 6
portrait = Image.open('img/dr-hafsa-patel.webp').convert('RGB')
scale = max(pw / portrait.width, ph / portrait.height)
portrait = portrait.resize((round(portrait.width * scale), round(portrait.height * scale)), Image.LANCZOS)
ox = (portrait.width - pw) // 2
oy = int((portrait.height - ph) * 0.2)
portrait = portrait.crop((ox, oy, ox + pw, oy + ph))
mask = Image.new('L', (pw, ph), 0)
md = ImageDraw.Draw(mask)
md.ellipse((0, 0, pw, pw), fill=255)
md.rectangle((0, pw // 2, pw, ph), fill=255)
# outer gold arch + cream gap
for pad, col in ((14, GOLD), (9, GREEN_900), (5, GOLD)):
    d.ellipse((px - pad, py - pad, px + pw + pad, py + pw + pad), fill=col)
    d.rectangle((px - pad, py + pw // 2, px + pw + pad, py + ph + pad), fill=col)
img.paste(portrait, (px, py), mask)

# logo tile
logo = Image.open('logo.png').convert('RGBA')
logo.thumbnail((112, 112), Image.LANCZOS)
tile = (70, 62, 70 + 140, 62 + 128)
d.rounded_rectangle(tile, radius=22, fill=CREAM)
img.paste(logo, (tile[0] + (140 - logo.width) // 2, tile[1] + (128 - logo.height) // 2), logo)

# text
serif_b = ImageFont.truetype(F + 'georgiab.ttf', 62)
serif = ImageFont.truetype(F + 'georgia.ttf', 30)
sans_b = ImageFont.truetype(F + 'Candarab.ttf', 22)
sans = ImageFont.truetype(F + 'Candara.ttf', 25)

x = 72
y = 222
d.text((x, y), 'A&Z Healthcare', font=serif_b, fill=CREAM)
d.text((x, y + 70), 'Centre', font=serif_b, fill=CREAM)


def spaced(draw, xy, text, font, fill, spacing):
    cx, cy = xy
    for ch in text:
        draw.text((cx, cy), ch, font=font, fill=fill)
        cx += draw.textlength(ch, font=font) + spacing


spaced(d, (x + 2, y + 160), 'UNANI CLINIC  ·  JOGESHWARI WEST, MUMBAI', sans_b, GOLD, 2.2)
d.line((x, y + 200, x + 520, y + 200), fill=GOLD + (0,), width=0)
d.text((x, y + 212), 'Dr. Hafsa Patel  ·  MD. Medicine in Unani', font=serif, fill=CREAM_GOLD)

# pill
pill_text = 'Hijama  ·  Unani consultation  ·  Online 10 AM – 10 PM'
tw = d.textlength(pill_text, font=sans)
d.rounded_rectangle((x, y + 272, x + tw + 44, y + 318), radius=23, outline=GOLD, width=2)
d.text((x + 22, y + 281), pill_text, font=sans, fill=CREAM)

img.save('img/share.jpg', 'JPEG', quality=86, optimize=True, progressive=True)
print('saved img/share.jpg')
