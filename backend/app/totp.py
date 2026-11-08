"""Códigos de un solo uso basados en tiempo (TOTP, RFC 6238), compatibles con
Google Authenticator, Microsoft Authenticator, Aegis, etc. Sin dependencias externas."""
import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

PERIODO = 30
DIGITOS = 6


def generar_secreto() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii")


def _codigo(secreto: str, paso: int) -> str:
    clave = base64.b32decode(secreto, casefold=True)
    digest = hmac.new(clave, struct.pack(">Q", paso), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    valor = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(valor % (10 ** DIGITOS)).zfill(DIGITOS)


def paso_actual(ahora=None) -> int:
    return int((time.time() if ahora is None else ahora) // PERIODO)


def verificar(secreto: str, codigo: str, ultimo_paso=None, ahora=None):
    """Devuelve el paso usado si el código es válido (con ±1 periodo de margen) y no
    se ha usado antes; si no, None. Guardar el paso devuelto evita reutilizar un código."""
    codigo = (codigo or "").replace(" ", "")
    if not (codigo.isdigit() and len(codigo) == DIGITOS) or not secreto:
        return None
    actual = paso_actual(ahora)
    for paso in (actual - 1, actual, actual + 1):
        if ultimo_paso is not None and paso <= ultimo_paso:
            continue
        if hmac.compare_digest(_codigo(secreto, paso), codigo):
            return paso
    return None


def uri_aprovisionamiento(secreto: str, email: str, emisor: str = "Davem Cyber Consulting") -> str:
    etiqueta = quote(f"{emisor}:{email}")
    return f"otpauth://totp/{etiqueta}?secret={secreto}&issuer={quote(emisor)}&algorithm=SHA1&digits={DIGITOS}&period={PERIODO}"


def qr_data_uri(texto: str):
    """QR en SVG como data URI. Si la librería no está instalada, devuelve None y se usa la clave manual."""
    try:
        import segno
    except ImportError:
        return None
    return segno.make(texto, error="m").svg_data_uri(scale=5, dark="#14213d", light="#ffffff")
