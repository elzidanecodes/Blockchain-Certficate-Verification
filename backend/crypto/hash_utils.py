import hashlib

def generate_md5_hash(data):
    return hashlib.md5(data.encode()).hexdigest()