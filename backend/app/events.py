from flask import request
from flask_login import current_user

from .extensions import db
from .models import SecurityEvent

ETIQUETAS = {
    "registro": "Registro de cuenta",
    "login_ok": "Inicio de sesión correcto",
    "login_fallido": "Inicio de sesión fallido",
    "2fa_ok": "Código 2FA correcto",
    "2fa_fallido": "Código 2FA incorrecto",
    "2fa_activado": "Doble factor activado",
    "logout": "Cierre de sesión",
    "limite_superado": "Demasiados intentos (bloqueo temporal)",
    "acceso_denegado": "Acceso denegado",
    "admin_estado": "Cambio de estado de solicitud",
}


def registrar_evento(tipo, email=None, user=None, detalle=None):
    """Guarda un evento de seguridad. Nunca debe romper la petición si falla."""
    try:
        if user is None and current_user and current_user.is_authenticated:
            user = current_user
        evento = SecurityEvent(
            tipo=tipo,
            email=(email or (user.email if user else None)),
            user_id=(user.id if user else None),
            ip=(request.remote_addr or "")[:45],
            ruta=request.path[:200],
            detalle=(detalle or "")[:300] or None,
        )
        db.session.add(evento)
        db.session.commit()
    except Exception:  # noqa: BLE001
        db.session.rollback()
