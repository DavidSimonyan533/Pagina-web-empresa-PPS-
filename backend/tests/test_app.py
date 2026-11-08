import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def client():
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
        yield app.test_client()
        db.drop_all()


def registrar(client, email="ana@example.com", password="una-frase-bien-larga-1"):
    return client.post(
        "/registro",
        data={
            "nombre": "Ana",
            "email": email,
            "empresa": "Ejemplo SL",
            "password": password,
            "confirmar": password,
            "acepto": "y",
        },
    )


def test_paginas_publicas(client):
    for ruta in ["/", "/servicios", "/sobre-nosotros", "/blog", "/contacto", "/privacidad", "/login", "/registro", "/health"]:
        assert client.get(ruta).status_code == 200, ruta


def test_404(client):
    assert client.get("/no-existe").status_code == 404


def test_area_cliente_requiere_login(client):
    r = client.get("/cliente/")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_registro_y_login(client):
    assert registrar(client).status_code == 302
    r = client.post("/login", data={"email": "ana@example.com", "password": "una-frase-bien-larga-1"})
    assert r.status_code == 302
    assert client.get("/cliente/").status_code == 200


def test_login_incorrecto(client):
    registrar(client)
    r = client.post("/login", data={"email": "ana@example.com", "password": "otra-contrasena-cualquiera"})
    assert r.status_code == 401


def test_contrasena_corta_rechazada(client):
    r = registrar(client, password="corta")
    assert r.status_code == 200  # vuelve al formulario con errores


def test_no_redirige_a_sitios_externos(client):
    registrar(client)
    r = client.post(
        "/login?next=https://evil.example",
        data={"email": "ana@example.com", "password": "una-frase-bien-larga-1"},
    )
    assert "evil.example" not in r.headers["Location"]


def test_cabeceras_de_seguridad(client):
    r = client.get("/")
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"


def test_solicitar_auditoria(client):
    registrar(client)
    client.post("/login", data={"email": "ana@example.com", "password": "una-frase-bien-larga-1"})
    r = client.post(
        "/cliente/solicitar-auditoria",
        data={"servicio": "ens", "tamano": "10-49", "descripcion": "Somos proveedores de una administración pública."},
    )
    assert r.status_code == 302
    assert b"Esquema Nacional" in client.get("/cliente/").data
