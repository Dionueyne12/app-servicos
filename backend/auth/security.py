from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import os

from app.config import settings
from utils.exceptions import UnauthorizedError


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"pbkdf2_sha256$120000${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = _b64decode(salt_b64)
        expected = _b64decode(digest_b64)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {"sub": subject, "exp": int(expires_at.timestamp())}
    return _encode_jwt(payload)


def decode_access_token(token: str) -> dict:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise UnauthorizedError("Token de acesso invalido.") from exc

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_signature = _sign(signing_input)
    received_signature = _b64decode(signature_b64)
    if not hmac.compare_digest(expected_signature, received_signature):
        raise UnauthorizedError("Token de acesso invalido.")

    payload = json.loads(_b64decode(payload_b64))
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise UnauthorizedError("Token de acesso expirado.")

    return payload


def _encode_jwt(payload: dict) -> str:
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    header_b64 = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature_b64 = _b64encode(_sign(signing_input))
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def _sign(value: bytes) -> bytes:
    return hmac.new(settings.jwt_secret_key.encode("utf-8"), value, hashlib.sha256).digest()


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))
