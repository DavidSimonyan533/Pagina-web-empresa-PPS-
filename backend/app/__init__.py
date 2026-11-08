import click
from flask import Flask, render_template

from .config import Config
from .extensions import csrf, db, limiter, login_manager
from .security import hash_password


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Falta SECRET_KEY. Copia .env.example a .env y rellénalo.")
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("Faltan las variables POSTGRES_* en el archivo .env.")

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para acceder a esta página."
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    from . import admin, auth, cliente, main
    from . import models  # noqa: F401  (registra las tablas)

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(cliente.bp)
    app.register_blueprint(admin.bp)

    from .content import euros
    app.jinja_env.filters["euros"] = euros

    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request_is_private():
            response.headers["Cache-Control"] = "no-store"
        return response

    def error_page(codigo, titulo, texto):
        return render_template("error.html", codigo=codigo, titulo=titulo, texto=texto), codigo

    @app.errorhandler(403)
    def forbidden(_):
        return error_page(403, "Acceso no permitido", "No tienes permiso para ver esta página.")

    @app.errorhandler(404)
    def not_found(_):
        return error_page(404, "Página no encontrada", "La dirección no existe o ha cambiado de sitio.")

    @app.errorhandler(413)
    def too_large(_):
        return error_page(413, "Envío demasiado grande", "Reduce el tamaño del mensaje e inténtalo de nuevo.")

    @app.errorhandler(429)
    def too_many(_):
        from .events import registrar_evento
        registrar_evento("limite_superado")
        return error_page(429, "Demasiados intentos", "Espera un minuto antes de volver a intentarlo.")

    @app.errorhandler(500)
    def server_error(_):
        db.session.rollback()
        return error_page(500, "Algo ha fallado", "Inténtalo de nuevo en unos minutos.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt="Correo del administrador")
    @click.option("--nombre", prompt="Nombre", default="Administrador")
    @click.password_option(help="Contraseña de al menos 12 caracteres")
    def create_admin(email, nombre, password):
        """Crea (o convierte en administrador) una cuenta. Solo lo ejecuta quien tiene acceso a la máquina."""
        if len(password) < 12:
            raise click.ClickException("La contraseña debe tener al menos 12 caracteres.")
        email = email.strip().lower()
        user = models.User.query.filter_by(email=email).first()
        if user is None:
            user = models.User(nombre=nombre.strip(), email=email)
            db.session.add(user)
        user.password_hash = hash_password(password)
        user.is_admin = True
        db.session.commit()
        click.echo(f"Administrador preparado: {email}")
        click.echo("Al entrar en /admin te pedirá activar el doble factor.")

    @app.cli.command("reset-2fa")
    @click.option("--email", prompt="Correo de la cuenta")
    def reset_2fa(email):
        """Desactiva el doble factor de una cuenta (por si se pierde el móvil)."""
        user = models.User.query.filter_by(email=email.strip().lower()).first()
        if user is None:
            raise click.ClickException("No existe ninguna cuenta con ese correo.")
        user.totp_secret = None
        user.totp_last_step = None
        db.session.commit()
        click.echo(f"Doble factor desactivado para {user.email}. Vuelve a activarlo al entrar en /admin.")

    return app


def request_is_private():
    """Las páginas de sesión, cliente y administración no deben quedar en caché."""
    from flask import request
    return request.path.startswith(("/cliente", "/admin", "/login", "/registro", "/logout"))
