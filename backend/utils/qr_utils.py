from urllib.parse import urlparse, parse_qs
from pyzbar.pyzbar import decode

def extract_certificate_id_from_qr(image):
    decoded_objects = decode(image)
    for obj in decoded_objects:
        data = obj.data.decode("utf-8")
        if data.startswith("https://127.0.0.1:5000"):
            parsed_url = urlparse(data)
            query = parse_qs(parsed_url.query)
            return query.get("certificate_id", [None])[0]
    return None