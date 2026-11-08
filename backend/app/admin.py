from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .content import get_service
from .extensions import db
from .models import AuditRequest, ContactMessage, User

bp = Blueprint("admin", __name__, url_prefix="/admin")

ESTADOS = ["Recibida", "En estudio", "Propuesta enviada", "En curso", "Cerrada"]


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@bp.route("/")
@admin_required
def panel():
    return render_template(
        "admin.html",
        solicitudes=AuditRequest.query.order_by(AuditRequest.creado.desc()).all(),
        mensajes=ContactMessage.query.order_by(ContactMessage.creado.desc()).all(),
        usuarios=User.query.order_by(User.creado.desc()).all(),
        estados=ESTADOS,
        get_service=get_service,
    )


@bp.route("/solicitud/<int:solicitud_id>/estado", methods=["POST"])
@admin_required
def estado(solicitud_id):
    solicitud = db.get_or_404(AuditRequest, solicitud_id)
    nuevo = request.form.get("estado", "")
    if nuevo in ESTADOS:
        solicitud.estado = nuevo
        db.session.commit()
        flash("Estado actualizado.", "success")
    else:
        flash("Estado no válido.", "error")
    return redirect(url_for("admin.panel"))
