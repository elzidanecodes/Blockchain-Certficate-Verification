
import base64
import io
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FONT_DIR = os.path.join(os.path.dirname(BASE_DIR), "static", "font")
TEMPLATE_PATH = os.path.join(os.path.dirname(BASE_DIR), "static", "pect_template.png")

# Regenerate sertifikat terverifikasi
def regenerate_verified_certificate(data, certificate_id):
    
    safe_data = {k: str(v) for k, v in data.items()}

    # Tambahkan key kosong jika tidak tersedia
    for key in ["listening", "reading", "total_lr", "writing", "total_writing"]:
        safe_data.setdefault(key, "")

    
    # Load template
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError("Template sertifikat tidak ditemukan")

    img = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        font_path = os.path.join(FONT_DIR, "Montserrat-SemiBold.ttf")
        font = ImageFont.truetype(font_path, 25)
    except:
        font = ImageFont.load_default()

    # 🖊️ Tulis ulang seluruh data ke template
    draw.text((1005, 454), safe_data["no_sertifikat"], font=font, fill="black")
    draw.text((415, 502), safe_data["name"], font=font, fill="black")
    draw.text((415, 536), safe_data["student_id"], font=font, fill="black")
    draw.text((1225, 502), safe_data["department"], font=font, fill="black")
    draw.text((1225, 536), safe_data["test_date"], font=font, fill="black")

    draw.text((640, 655), safe_data["listening"], font=font, fill="black")
    draw.text((980, 655), safe_data["reading"], font=font, fill="black")
    draw.text((1310, 655), safe_data["total_lr"], font=font, fill="black")
    draw.text((830, 948), safe_data["writing"], font=font, fill="black")
    draw.text((1130, 948), safe_data["total_writing"], font=font, fill="black")

    # Generate QR final → link publik
    qr_data = f"https://localhost:5173/verify/{certificate_id}"
    qr_img = qrcode.make(qr_data).convert("RGBA").resize((200, 200))

    # Transparan background putih
    datas = qr_img.getdata()
    newData = []
    for item in datas:
        if item[:3] == (255, 255, 255):
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    qr_img.putdata(newData)

    img.paste(qr_img, (880, 1090), qr_img)

    # Tambahkan tanda tangan
    try:
        ttd_img = Image.open("static/ttd.png").convert("RGBA").resize((250, 100))
        img.paste(ttd_img, (350, 1140), ttd_img)
        img.paste(ttd_img, (1400, 1140), ttd_img)
    except Exception as e:
        print("⚠️ Gagal pasang tanda tangan:", e)

    # Simpan image ke buffer dan encode base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    

    # QR juga ke base64 untuk disimpan
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode("utf-8")

    return img_bytes, img_base64, qr_base64