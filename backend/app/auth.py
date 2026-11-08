import time

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from . import totp
from .events import registrar_evento
from .extensions import db, limiter
from .forms import CodigoForm, LoginForm, RegisterForm
from .models import User
from .security import hash_password, is_safe_next, verify_password

bp = Blueprint("auth", __name__)

PLAZO_2FA = 300  # segundos para introducir el código tras la contraseña


def _destino(next_url):
    return next_url if is_safe_next(next_url) else url_for("cliente.area")


@bp.route("/registro", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("cliente.area"))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User(
            nombre=form.nombre.data.strip(),
            email=email,
            empresa=(form.empresa.data or "").strip() or None,
            password_hash=hash_password(form.password.data),
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("No hemos podido crear la cuenta con esos datos.", "error")
            return render_template("registro.html", form=form), 400
        registrar_evento("registro", user=user)
        flash("Cuenta creada. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))
    return render_template("registro.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("cliente.area"))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if verify_password(user.password_hash if user else None, form.password.data):
            destino = _destino(request.args.get("next"))
            if user.tiene_2fa:
                session.clear()
                session["2fa_user"] = user.id
                session["2fa_hasta"] = time.time() + PLAZO_2FA
                session["2fa_next"] = destino
                return redirect(url_for("auth.login_2fa"))
            session.clear()
            login_user(user)
            session.permanent = True
            registrar_evento("login_ok", user=user)
            return redirect(destino)
        registrar_evento("login_fallido", email=email)
        flash("Correo o contraseña incorrectos.", "error")
        return render_template("login.html", form=form), 401
    return render_template("login.html", form=form)


@bp.route("/login/verificacion", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login_2fa():
    user_id = session.get("2fa_user")
    if not user_id or time.time() > session.get("2fa_hasta", 0):
        session.pop("2fa_user", None)
        flash("La verificación ha caducado. Vuelve a iniciar sesión.", "info")
        return redirect(url_for("auth.login"))
    user = db.session.get(User, user_id)
    if user is None or not user.tiene_2fa:
        session.clear()
        return redirect(url_for("auth.login"))

    form = CodigoForm()
    if form.validate_on_submit():
        paso = totp.verificar(user.totp_secret, form.codigo.data, user.totp_last_step)
        if paso is not None:
            user.totp_last_step = paso
            db.session.commit()
            destino = session.get("2fa_next") or url_for("cliente.area")
            session.clear()
            login_user(user)
            session.permanent = True
            registrar_evento("2fa_ok", user=user)
            registrar_evento("login_ok", user=user, detalle="Con doble factor")
            return redirect(destino if is_safe_next(destino) else url_for("cliente.area"))
        registrar_evento("2fa_fallido", user=user)
        flash("Código incorrecto o ya utilizado.", "error")
        return render_template("login_2fa.html", form=form), 401
    return render_template("login_2fa.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    registrar_evento("logout")
    logout_user()
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("main.index"))
