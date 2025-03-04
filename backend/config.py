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
    
# Load ABI contract
base_dir = os.path.dirname(os.path.abspath(__file__))
contract_path = os.path.join(base_dir, '../blockchain/build/contracts/CertificateVerification.json')

with open(contract_path) as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = web3.eth.contract(address=contract_address, abi=contract_abi)