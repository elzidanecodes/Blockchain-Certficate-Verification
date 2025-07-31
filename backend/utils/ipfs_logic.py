# ipfs_logic.py
from crypto.aes_utils import decrypt_data
from config import AES_SECRET_KEY
from utils.image_logic import regenerate_verified_certificate
from ipfs.ipfs_utils import upload_to_ipfs

def regenerate_and_upload_ipfs(encrypted_data, certificate_id):
    # Dekripsi
    decrypted = decrypt_data(encrypted_data, AES_SECRET_KEY)
    if not decrypted:
        raise ValueError("Dekripsi gagal")

    # Regenerate image
    img_bytes, _, qr_base64 = regenerate_verified_certificate(decrypted, certificate_id)

    # Upload ke IPFS
    ipfs = upload_to_ipfs(img_bytes)
    if not ipfs:
        raise ValueError("Upload ke IPFS gagal")

    return {
        "decrypted_data": decrypted,
        "img_bytes": img_bytes,
        "qr_code": qr_base64,
        "ipfs_cid": ipfs.get("cid"),
        "ipfs_url": ipfs.get("url")
    }