import os
import hashlib
import hmac
from dotenv import load_dotenv

load_dotenv()

SHARED_SECRET_KEY = os.getenv("ZKP_SECRET_KEY", "default_insecure_secret").encode()

def generate_proof(officer_id: str, encrypted_query: str) -> str:
    message = f"{officer_id}:{encrypted_query}".encode()
    return hmac.new(SHARED_SECRET_KEY, message, hashlib.sha256).hexdigest()

def verify_proof(officer_id: str, encrypted_query: str, proof: str) -> bool:
    expected = generate_proof(officer_id, encrypted_query)
    return hmac.compare_digest(expected, proof)
