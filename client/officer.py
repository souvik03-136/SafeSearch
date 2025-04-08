from utils.zkp_sim import generate_proof
from utils.encryption import get_context, encrypt_query_string

officer_id = "agent007"
query = "murder"

context = get_context()
enc_query = encrypt_query_string(context, query)  # This returns encrypted string
proof = generate_proof(officer_id, enc_query)     # Use encrypted query in proof

# Send this as JSON
payload = {
    "officer_id": officer_id,
    "encrypted_query": enc_query,
    "proof": proof
}
