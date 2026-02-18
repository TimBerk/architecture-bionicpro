import base64
import hashlib
import os
from cryptography.fernet import Fernet


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def gen_code_verifier() -> str:
    # 32 bytes -> good entropy, base64url
    return b64url(os.urandom(32))


def code_challenge_s256(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return b64url(digest)


def gen_state() -> str:
    return b64url(os.urandom(16))


def _fernet_from_env() -> Fernet:
    key = os.environ["TOKEN_ENC_KEY"].encode("ascii")
    return Fernet(key)


def encrypt(token: str) -> str:
    return _fernet_from_env().encrypt(token.encode("utf-8")).decode("ascii")


def decrypt(token_enc: str) -> str:
    return _fernet_from_env().decrypt(token_enc.encode("ascii")).decode("utf-8")
