from datetime import datetime, timezone

from flask_login import UserMixin

from .extensions import db, login_manager


def _now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    empresa = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    totp_secret = db.Column(db.String(64))
    totp_last_step = db.Column(db.Integer)
    creado = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    solicitudes = db.relationship(
        "AuditRequest", backref="usuario", lazy=True, order_by="AuditRequest.creado.desc()"
    )

    @property
    def tiene_2fa(self):
        return bool(self.totp_secret)


class AuditRequest(db.Model):
    __tablename__ = "audit_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    servicio = db.Column(db.String(60), nullable=False)
    tamano = db.Column(db.String(30), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_preferida = db.Column(db.Date)
    estado = db.Column(db.String(30), default="Recibida", nullable=False)
    creado = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    asunto = db.Column(db.String(120), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    creado = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)


class SecurityEvent(db.Model):
    """Registro de eventos de seguridad: inicios de sesión, bloqueos, accesos denegados, cambios de admin."""
    __tablename__ = "security_events"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(40), nullable=False, index=True)
    email = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    ip = db.Column(db.String(45))
    ruta = db.Column(db.String(200))
    detalle = db.Column(db.String(300))
    creado = db.Column(db.DateTime(timezone=True), default=_now, nullable=False, index=True)


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
