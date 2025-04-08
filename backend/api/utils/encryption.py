import os
import base64
from typing import Union

import tenseal as ts
from dotenv import load_dotenv

load_dotenv()


def get_context() -> ts.Context:
    # read parameters from env, with defaults
    poly_mod_degree = int(os.getenv("CONTEXT_POLY_MOD_DEGREE", 8192))
    coeff_mod_bits = [
        int(x) for x in os.getenv("CONTEXT_COEFF_MOD_BITS", "60,40,40,60").split(",")
    ]
    global_scale_bits = int(os.getenv("CONTEXT_GLOBAL_SCALE_BITS", 40))

    ctx = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=poly_mod_degree,
        coeff_mod_bit_sizes=coeff_mod_bits,
    )
    ctx.global_scale = 2 ** global_scale_bits
    ctx.generate_galois_keys()
    return ctx


def encrypt_string(context: ts.Context, text: str) -> bytes:
    # convert each char to its lowercase ordinal
    vec = [float(ord(c)) for c in text.lower()]
    enc = ts.ckks_vector(context, vec)
    return enc.serialize()


def serialize_to_base64(blob: bytes) -> str:
    return base64.b64encode(blob).decode("utf-8")


def deserialize_from_base64(context: ts.Context, b64: str) -> ts.CKKSVector:
    blob = base64.b64decode(b64.encode("utf-8"))
    return ts.ckks_vector_from(context, blob)


def encrypted_compare(
    context: ts.Context,
    enc_b64_query: str,
    plaintext: str,
    threshold: float = 1e-3,
) -> bool:
    enc_query = deserialize_from_base64(context, enc_b64_query)
    vec_plain = [float(ord(c)) for c in plaintext.lower()]
    enc_text = ts.ckks_vector(context, vec_plain)

    # compute encrypted difference and decrypt
    enc_diff = enc_query - enc_text
    diff_vals = enc_diff.decrypt()
    distance = sum(abs(x) for x in diff_vals)
    return distance < threshold


if __name__ == "__main__":
    ctx = get_context()

    q = "HelloWorld"
    enc_bytes = encrypt_string(ctx, q)
    enc_b64 = serialize_to_base64(enc_bytes)
    print(f"Encrypted (base64): {enc_b64}")

    for candidate in ["helloworld", "hello_world", "hell0world"]:
        match = encrypted_compare(ctx, enc_b64, candidate)
        print(f"Compare to '{candidate}': {'MATCH' if match else 'DIFFER'}")
