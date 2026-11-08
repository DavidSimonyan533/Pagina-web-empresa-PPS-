from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from .extensions import db, limiter
from .forms import LoginForm, RegisterForm
from .models import User
from .security import hash_password, is_safe_next, verify_password

bp = Blueprint("auth", __name__)


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
            login_user(user)
            session.permanent = True
            target = request.args.get("next")
            return redirect(target if is_safe_next(target) else url_for("cliente.area"))
        flash("Correo o contraseña incorrectos.", "error")
        return render_template("login.html", form=form), 401
    return render_template("login.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("main.index"))
