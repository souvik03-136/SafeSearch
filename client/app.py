import os
import base64

from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

from utils.encryption import get_context, encrypt_query_string
from utils.zkp_sim import generate_proof

# load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "insecure_dev_key")

OFFICER_ID = os.getenv("OFFICER_ID", "default_officer")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query", "").lower()

        context = get_context()
        enc_query = encrypt_query_string(context, query)
        b64_enc_query = base64.b64encode(enc_query).decode("utf-8")

        proof = generate_proof(OFFICER_ID, b64_enc_query)

        try:
            resp = requests.post(
                f"{BACKEND_URL}/search",
                json={
                    "officer_id": OFFICER_ID,
                    "encrypted_query": b64_enc_query,
                    "proof": proof,
                },
                timeout=5,
            )
            resp.raise_for_status()
            return jsonify(resp.json())
        except requests.RequestException as e:
            return jsonify({"error": "backend request failed", "details": str(e)}), 502

    return render_template("index.html")


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    app.run(host=host, port=port)
