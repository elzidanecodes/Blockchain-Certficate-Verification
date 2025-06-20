import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))) 
from crypto.hash_utils import generate_md5_hash

def test_md5_hash_consistency():
    data = "23374/PL2.3/KM/2022|Laita Zidan|2141762100"
    hash1 = generate_md5_hash(data)
    hash2 = generate_md5_hash(data)
    
    assert hash1 == hash2, "❌ Hash tidak konsisten"