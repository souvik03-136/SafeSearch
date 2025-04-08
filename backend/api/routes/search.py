import os
import base64

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

import psycopg2
import tenseal as ts

from utils.zkp_sim import verify_proof
from utils.encryption import get_context

load_dotenv()

router = APIRouter()


class SearchRequest(BaseModel):
    officer_id: str
    encrypted_query: str
    proof: str


def get_db_connection():
    """Reads all connection params from env and returns a new psycopg2 connection."""
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def compare_encrypted(enc_query: ts.CKKSVector, plain_text: str, context: ts.Context) -> bool:
    """Decrypts the diff between two CKKS vectors and checks if within tolerance."""
    plain_vector = [float(ord(c)) for c in plain_text.lower()]
    enc_plain = ts.ckks_vector(context, plain_vector)
    diff = enc_query - enc_plain
    diff_vals = diff.decrypt()
    distance = sum(abs(x) for x in diff_vals)
    return distance < 1e-3


@router.post("/search")
async def secure_search(request: SearchRequest):
    officer_id = request.officer_id
    encrypted_query = request.encrypted_query
    proof = request.proof
    if not verify_proof(officer_id, encrypted_query, proof):
        raise HTTPException(status_code=403, detail="Invalid proof. Access denied.")
    context = get_context()

    try:
        enc_bytes = base64.b64decode(encrypted_query)
        enc_query = ts.ckks_vector_from(context, enc_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid encrypted query format.")
    matched = []
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, crime_type FROM crimes;")
        for crime_id, crime_type in cursor.fetchall():
            if compare_encrypted(enc_query, crime_type, context):
                matched.append({"id": crime_id, "crime_type": crime_type})
    finally:
        conn.close()

    return {"result_count": len(matched), "matches": matched}
