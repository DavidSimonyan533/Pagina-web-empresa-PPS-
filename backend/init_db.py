"""Crea las tablas y añade las columnas nuevas a una base de datos existente,
esperando a que PostgreSQL esté listo. Así no hace falta borrar los datos al actualizar."""
import sys
import time

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from app import create_app
from app.extensions import db

# Columnas añadidas después de la primera versión: (tabla, columna, definición SQL)
COLUMNAS_NUEVAS = [
    ("users", "is_admin", "BOOLEAN NOT NULL DEFAULT false"),
    ("users", "totp_secret", "VARCHAR(64)"),
    ("users", "totp_last_step", "INTEGER"),
]


def migrar():
    db.create_all()
    inspector = inspect(db.engine)
    with db.engine.begin() as conn:
        for tabla, columna, definicion in COLUMNAS_NUEVAS:
            existentes = {c["name"] for c in inspector.get_columns(tabla)}
            if columna not in existentes:
                conn.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}"))
                print(f"Columna añadida: {tabla}.{columna}")


app = create_app()

with app.app_context():
    for _ in range(30):
        try:
            migrar()
            print("Base de datos lista.")
            break
        except OperationalError:
            print("Esperando a la base de datos...")
            time.sleep(2)
    else:
        print("No se pudo conectar con la base de datos.")
        sys.exit(1)
