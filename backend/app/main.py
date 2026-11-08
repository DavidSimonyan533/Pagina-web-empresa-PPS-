from flask import Blueprint, abort, flash, redirect, render_template, url_for

from .content import (
    CREDENCIALES, DIAGNOSTICO, ESCENARIOS, FACTOR_PLAZO, FUNDADOR, FACTOR_TAMANO, FAQ, PACKS, POSTS, PROCESS, SERVICES, VALORES, get_post, get_service,
)
from .extensions import db, limiter
from .forms import ContactForm
from .models import ContactMessage

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template(
        "index.html",
        services=SERVICES,
        process=PROCESS,
        posts=POSTS[:2],
        credenciales=CREDENCIALES,
        valores=VALORES,
        diagnostico=DIAGNOSTICO,
        escenarios=ESCENARIOS,
        get_service=get_service,
    )


@bp.route("/servicios")
def servicios():
    return render_template("servicios.html", services=SERVICES)


@bp.route("/sobre-nosotros")
def sobre():
    return render_template("sobre.html", valores=VALORES, credenciales=CREDENCIALES, fundador=FUNDADOR)


@bp.route("/blog")
def blog():
    return render_template("blog.html", posts=POSTS)


@bp.route("/blog/<slug>")
def blog_post(slug):
    post = get_post(slug)
    if post is None:
        abort(404)
    return render_template("blog_post.html", post=post)


@bp.route("/contacto", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def contacto():
    form = ContactForm()
    if form.validate_on_submit():
        db.session.add(
            ContactMessage(
                nombre=form.nombre.data.strip(),
                email=form.email.data.strip().lower(),
                asunto=form.asunto.data.strip(),
                mensaje=form.mensaje.data.strip(),
            )
        )
        db.session.commit()
        flash("Mensaje enviado. Te responderemos lo antes posible.", "success")
        return redirect(url_for("main.contacto"))
    return render_template("contacto.html", form=form)


@bp.route("/tarifas")
def tarifas():
    return render_template(
        "tarifas.html", packs=PACKS, services=SERVICES, tamanos=FACTOR_TAMANO, plazos=FACTOR_PLAZO
    )


@bp.route("/preguntas-frecuentes")
def faq():
    return render_template("faq.html", faq=FAQ)


@bp.route("/aviso-legal")
def aviso_legal():
    return render_template("aviso_legal.html")


@bp.route("/cookies")
def cookies():
    return render_template("cookies.html")


@bp.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")


@bp.route("/health")
def health():
    return "ok", 200
