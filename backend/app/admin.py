from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from . import totp
from .content import get_service
from .events import ETIQUETAS, registrar_evento
from .extensions import db, limiter
from .forms import CodigoForm
from .models import AuditRequest, ContactMessage, SecurityEvent, User

bp = Blueprint("admin", __name__, url_prefix="/admin")

ESTADOS = ["Recibida", "En estudio", "Propuesta enviada", "En curso", "Cerrada"]


def _solo_admin():
    if not current_user.is_admin:
        registrar_evento("acceso_denegado", detalle="Intento de acceso a administración")
        abort(403)


def admin_required(view):
    """Exige cuenta de administrador CON doble factor activado."""
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        _solo_admin()
        if not current_user.tiene_2fa:
            flash("Activa el doble factor para usar el panel de administración.", "info")
            return redirect(url_for("admin.doble_factor"))
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
        seccion="panel",
    )


@bp.route("/solicitud/<int:solicitud_id>/estado", methods=["POST"])
@admin_required
def estado(solicitud_id):
    solicitud = db.get_or_404(AuditRequest, solicitud_id)
    nuevo = request.form.get("estado", "")
    if nuevo in ESTADOS:
        anterior = solicitud.estado
        solicitud.estado = nuevo
        db.session.commit()
        registrar_evento("admin_estado", detalle=f"Solicitud {solicitud.id}: {anterior} → {nuevo}")
        flash("Estado actualizado.", "success")
    else:
        flash("Estado no válido.", "error")
    return redirect(url_for("admin.panel"))


@bp.route("/seguridad")
@admin_required
def seguridad():
    tipo = request.args.get("tipo", "")
    consulta = SecurityEvent.query
    if tipo in ETIQUETAS:
        consulta = consulta.filter_by(tipo=tipo)
    eventos = consulta.order_by(SecurityEvent.creado.desc()).limit(300).all()
    resumen = {
        clave: SecurityEvent.query.filter_by(tipo=clave).count()
        for clave in ("login_fallido", "limite_superado", "acceso_denegado", "2fa_fallido")
    }
    return render_template(
        "admin_seguridad.html", eventos=eventos, etiquetas=ETIQUETAS, tipo=tipo, resumen=resumen, seccion="seguridad"
    )


@bp.route("/doble-factor", methods=["GET", "POST"])
@login_required
@limiter.limit("5 per minute", methods=["POST"])
def doble_factor():
    _solo_admin()
    if current_user.tiene_2fa:
        return render_template("admin_2fa.html", activo=True, seccion="2fa")

    secreto = session.get("totp_alta")
    if not secreto:
        secreto = totp.generar_secreto()
        session["totp_alta"] = secreto

    form = CodigoForm()
    if form.validate_on_submit():
        paso = totp.verificar(secreto, form.codigo.data)
        if paso is not None:
            current_user.totp_secret = secreto
            current_user.totp_last_step = paso
            db.session.commit()
            session.pop("totp_alta", None)
            registrar_evento("2fa_activado")
            flash("Doble factor activado. A partir de ahora te pediremos el código al entrar.", "success")
            return redirect(url_for("admin.panel"))
        registrar_evento("2fa_fallido", detalle="Durante la activación")
        flash("El código no coincide. Comprueba que la hora del móvil es correcta.", "error")

    uri = totp.uri_aprovisionamiento(secreto, current_user.email)
    clave = " ".join(secreto[i:i + 4] for i in range(0, len(secreto), 4))
    return render_template(
        "admin_2fa.html", activo=False, form=form, clave=clave, qr=totp.qr_data_uri(uri), seccion="2fa"
    )
