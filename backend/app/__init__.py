from flask import Flask, render_template

from .config import Config
from .extensions import csrf, db, limiter, login_manager


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

    from . import auth, cliente, main
    from . import models  # noqa: F401  (registra las tablas)

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(cliente.bp)

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
        if request_is_private(response):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", codigo=404, titulo="Página no encontrada",
                               texto="La dirección no existe o ha cambiado de sitio."), 404

    @app.errorhandler(429)
    def too_many(_):
        return render_template("error.html", codigo=429, titulo="Demasiados intentos",
                               texto="Espera un minuto antes de volver a intentarlo."), 429

    @app.errorhandler(413)
    def too_large(_):
        return render_template("error.html", codigo=413, titulo="Envío demasiado grande",
                               texto="Reduce el tamaño del mensaje e inténtalo de nuevo."), 413

    @app.errorhandler(500)
    def server_error(_):
        return render_template("error.html", codigo=500, titulo="Algo ha fallado",
                               texto="Hemos registrado el problema. Inténtalo de nuevo en unos minutos."), 500

    return app


def request_is_private(response):
    """Las páginas de sesión y de cliente no deben quedar en caché."""
    from flask import request
    return request.path.startswith(("/cliente", "/login", "/registro", "/logout"))
