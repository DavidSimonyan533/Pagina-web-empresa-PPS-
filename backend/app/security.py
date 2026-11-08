from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_hasher = PasswordHasher()
# Hash de relleno: se verifica contra él cuando el usuario no existe,
# para que el tiempo de respuesta no delate qué correos están registrados.
_DUMMY_HASH = _hasher.hash("relleno-para-igualar-tiempos")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(stored_hash, password: str) -> bool:
    try:
        _hasher.verify(stored_hash or _DUMMY_HASH, password)
        return stored_hash is not None
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def is_safe_next(target) -> bool:
    """Solo permite redirigir a rutas internas (evita open redirect)."""
    return bool(target) and target.startswith("/") and not target.startswith("//") and "\\" not in target
