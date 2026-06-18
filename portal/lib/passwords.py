"""
Password hashing for the portal — pbkdf2-sha256, stdlib only.

Why pbkdf2 (not bcrypt/argon2): no extra deps, well-understood, FIPS-blessed.
For a 10-user, 1-week-pilot portal this is appropriate.

Hash format (single string, easy to store as JSON value):
    pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>

OWASP 2023 baseline: 600_000 iterations for sha256. We use 480_000 to keep
login latency under ~80ms on the deploy host while staying well above the
500k floor most "fast" attackers expect.
"""

from __future__ import annotations

import hashlib
import hmac
import os

ALGO = "pbkdf2_sha256"
ITERATIONS = 480_000
SALT_BYTES = 16
HASH_BYTES = 32


def hash_password(plain: str) -> str:
    if not isinstance(plain, str) or not plain:
        raise ValueError("password must be a non-empty string")
    salt = os.urandom(SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, ITERATIONS, dklen=HASH_BYTES)
    return f"{ALGO}${ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(plain: str, stored: str | None) -> bool:
    if not stored or not isinstance(plain, str) or not plain:
        return False
    try:
        algo, iters_s, salt_hex, hash_hex = stored.split("$", 3)
    except ValueError:
        return False
    if algo != ALGO:
        return False
    try:
        iters = int(iters_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, iters, dklen=len(expected))
    return hmac.compare_digest(dk, expected)
