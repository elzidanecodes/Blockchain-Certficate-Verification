import os
from dotenv import load_dotenv
import json
from web3 import Web3

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GANACHE_URL = os.getenv("GANACHE_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))


# Cek koneksi
if web3.is_connected():
    print("Connected to Ganache")
else:
    print("Failed to connect to Ganache")
    
