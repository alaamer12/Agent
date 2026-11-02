"""Create fixture assets for testing the assets skill scripts."""
import os
from PIL import Image, ImageDraw

root = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(root, "raw"), exist_ok=True)
os.makedirs(os.path.join(root, "app"), exist_ok=True)

# A square logo: blue rounded square with a white circle.
logo = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
draw = ImageDraw.Draw(logo)
draw.rounded_rectangle((0, 0, 1023, 1023), radius=180, fill=(37, 99, 235, 255))
draw.ellipse((312, 312, 712, 712), fill=(255, 255, 255, 255))
logo.save(os.path.join(root, "raw", "logo.png"))

# A gradient/blue banner with anti-aliased white text-like shapes.
banner = Image.new("RGB", (800, 300), (37, 99, 235))
draw = ImageDraw.Draw(banner)
for x in range(0, 800, 8):
    shade = 60 + x * 120 // 800
    draw.rectangle((x, 0, x + 8, 300), fill=(shade, 99, 235))
draw.rectangle((60, 120, 500, 180), fill=(15, 23, 42))
draw.ellipse((700, 60, 780, 140), fill=(255, 255, 255))
banner.save(os.path.join(root, "raw", "banner.png"))

# A JPEG photo-like image.
photo = Image.new("RGB", (1600, 900), (20, 120, 80))
draw = ImageDraw.Draw(photo)
draw.rectangle((200, 200, 900, 700), fill=(240, 200, 60))
photo.save(os.path.join(root, "raw", "photo.jpg"), quality=95)

# A PNG that lies about its extension (real bytes are PNG).
logo.save(os.path.join(root, "raw", "mislabelled.jpg"), format="PNG")

# Text files that reference assets and external URLs.
with open(os.path.join(root, "app", "index.html"), "w", encoding="utf-8") as f:
    f.write("""<html>
<head>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">
<link rel="icon" href="/icons/favicon.ico">
</head>
<body>
<img src="https://cdn.example.com/media/photo.png" alt="photo">
<img src="assets/logo.png" alt="logo">
<script src="app.js"></script>
</body></html>""")

with open(os.path.join(root, "app", "styles.css"), "w", encoding="utf-8") as f:
    f.write(""".brand { background: url('../raw/banner.png'); }\n.photo { background: url('https://cdn.example.com/fonts/Inter.woff2'); }\n""")

with open(os.path.join(root, "vendor-assets.txt"), "w", encoding="utf-8") as f:
    f.write("https://cdn.example.com/logo.png icons/logo.png\nhttps://cdn.example.com/fonts/Inter.woff2 fonts/Inter.woff2\n")

print("fixtures created under", root)
