import requests

def upload_to_ipfs(file_bytes, filename="certificate.png"):
    try:
        files = {'file': (filename, file_bytes)}
        res = requests.post("http://127.0.0.1:5001/api/v0/add", files=files)
        res.raise_for_status()
        cid = res.json()["Hash"]
        return cid
    except Exception as e:
        print(f"❌ IPFS upload error: {e}")
        return None