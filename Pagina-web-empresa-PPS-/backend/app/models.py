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
    creado = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    solicitudes = db.relationship(
        "AuditRequest", backref="usuario", lazy=True, order_by="AuditRequest.creado.desc()"
    )


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


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
