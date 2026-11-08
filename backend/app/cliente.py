from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from .content import get_service
from .extensions import db
from .forms import AuditRequestForm
from .models import AuditRequest

bp = Blueprint("cliente", __name__, url_prefix="/cliente")


@bp.route("/")
@login_required
def area():
    return render_template("area_cliente.html", get_service=get_service)


@bp.route("/solicitar-auditoria", methods=["GET", "POST"])
@login_required
def solicitar():
    form = AuditRequestForm()
    if form.validate_on_submit():
        db.session.add(
            AuditRequest(
                user_id=current_user.id,
                servicio=form.servicio.data,
                tamano=form.tamano.data,
                fecha_preferida=form.fecha_preferida.data,
                descripcion=form.descripcion.data.strip(),
            )
        )
        db.session.commit()
        flash("Solicitud recibida. Nos pondremos en contacto contigo.", "success")
        return redirect(url_for("cliente.area"))
    return render_template("solicitar.html", form=form)
