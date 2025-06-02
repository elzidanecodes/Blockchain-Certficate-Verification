from config import GATEWAY_URL, IPFS_API
import requests

def upload_to_ipfs(file_bytes, filename="certificate.png"):
    try:
        files = {'file': (filename, file_bytes)}
        res = requests.post(f"{IPFS_API}/api/v0/add", files=files)
        res.raise_for_status()
        cid = res.json()["Hash"]
        
        # Delete duplikat file
        requests.post(f"{IPFS_API}/api/v0/files/rm", params={
            "arg": f"/verified/{filename}",
            "force": True
        })
        
        # Tambahkan file ke MFS IPFS Desktop
        requests.post(f"{IPFS_API}/api/v0/files/cp", params={
            "arg": f"/ipfs/{cid}",
            "arg": f"/verified/{filename}"
        })
        return {
            "cid": cid,
            "url": f"{GATEWAY_URL}{cid}"
        }
    except Exception as e:
        print(f"❌ IPFS upload error: {e}")
        return None