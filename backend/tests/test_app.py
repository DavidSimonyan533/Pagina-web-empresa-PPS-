import pytest

from app import create_app, totp
from app.extensions import db
from app.models import SecurityEvent, User
from app.security import hash_password

PASS = "una-frase-bien-larga-1"
ADMIN_PASS = "otra-frase-muy-larga-2"


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "clave-de-pruebas",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "RATELIMIT_ENABLED": False,
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def registrar(client, email="ana@example.com", password=PASS):
    return client.post(
        "/registro",
        data={"nombre": "Ana", "email": email, "empresa": "Ejemplo SL",
              "password": password, "confirmar": password, "acepto": "y"},
    )


def entrar(client, email="ana@example.com", password=PASS):
    return client.post("/login", data={"email": email, "password": password})


def crear_admin(secreto=None):
    u = User(nombre="Admin", email="admin@example.com", password_hash=hash_password(ADMIN_PASS),
             is_admin=True, totp_secret=secreto)
    db.session.add(u)
    db.session.commit()
    return u


def codigo_actual(secreto):
    return totp._codigo(secreto, totp.paso_actual())


def test_paginas_publicas(client):
    rutas = ["/", "/servicios", "/tarifas", "/sobre-nosotros", "/blog", "/contacto", "/privacidad",
             "/preguntas-frecuentes", "/aviso-legal", "/cookies", "/login", "/registro", "/health"]
    for ruta in rutas:
        assert client.get(ruta).status_code == 200, ruta


def test_404(client):
    assert client.get("/no-existe").status_code == 404


def test_area_cliente_requiere_login(client):
    r = client.get("/cliente/")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_registro_y_login(client):
    assert registrar(client).status_code == 302
    assert entrar(client).status_code == 302
    assert client.get("/cliente/").status_code == 200
    assert SecurityEvent.query.filter_by(tipo="login_ok").count() == 1


def test_login_incorrecto_queda_registrado(client):
    registrar(client)
    assert entrar(client, password="otra-contrasena-cualquiera").status_code == 401
    assert SecurityEvent.query.filter_by(tipo="login_fallido").count() == 1


def test_contrasena_corta_rechazada(client):
    assert registrar(client, password="corta").status_code == 200


def test_no_redirige_a_sitios_externos(client):
    registrar(client)
    r = client.post("/login?next=https://evil.example", data={"email": "ana@example.com", "password": PASS})
    assert "evil.example" not in r.headers["Location"]


def test_cabeceras_de_seguridad(client):
    r = client.get("/")
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"


def test_solicitar_auditoria(client):
    registrar(client)
    entrar(client)
    r = client.post("/cliente/solicitar-auditoria",
                    data={"servicio": "ens", "tamano": "10-49", "descripcion": "Somos proveedores de una administración pública."})
    assert r.status_code == 302
    assert "Esquema Nacional".encode() in client.get("/cliente/").data


def test_cliente_no_entra_en_admin(client):
    registrar(client)
    entrar(client)
    assert client.get("/admin/").status_code == 403
    assert SecurityEvent.query.filter_by(tipo="acceso_denegado").count() == 1


def test_admin_sin_2fa_debe_activarlo(client):
    crear_admin()
    entrar(client, "admin@example.com", ADMIN_PASS)
    r = client.get("/admin/")
    assert r.status_code == 302 and "/admin/doble-factor" in r.headers["Location"]

    client.get("/admin/doble-factor")
    with client.session_transaction() as s:
        secreto = s["totp_alta"]
    r = client.post("/admin/doble-factor", data={"codigo": codigo_actual(secreto)})
    assert r.status_code == 302
    assert client.get("/admin/").status_code == 200
    assert client.get("/admin/seguridad").status_code == 200


def test_login_admin_con_2fa(client):
    secreto = totp.generar_secreto()
    crear_admin(secreto)
    r = entrar(client, "admin@example.com", ADMIN_PASS)
    assert "/login/verificacion" in r.headers["Location"]
    assert client.get("/admin/").status_code == 302  # aún no ha iniciado sesión

    assert client.post("/login/verificacion", data={"codigo": "000000" if codigo_actual(secreto) != "000000" else "111111"}).status_code == 401
    r = client.post("/login/verificacion", data={"codigo": codigo_actual(secreto)})
    assert r.status_code == 302
    assert client.get("/admin/").status_code == 200


def test_codigo_2fa_no_reutilizable(client):
    secreto = totp.generar_secreto()
    crear_admin(secreto)
    codigo = codigo_actual(secreto)
    entrar(client, "admin@example.com", ADMIN_PASS)
    client.post("/login/verificacion", data={"codigo": codigo})
    client.post("/logout")
    entrar(client, "admin@example.com", ADMIN_PASS)
    assert client.post("/login/verificacion", data={"codigo": codigo}).status_code == 401


def test_totp_vectores_rfc6238():
    import base64
    secreto = base64.b32encode(b"12345678901234567890").decode()
    assert totp._codigo(secreto, 59 // 30) == "287082"
    assert totp._codigo(secreto, 1111111109 // 30) == "081804"
