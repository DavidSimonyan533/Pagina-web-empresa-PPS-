"""Crea las tablas de la base de datos, esperando a que PostgreSQL esté listo."""
import sys
import time

from sqlalchemy.exc import OperationalError

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    for _ in range(30):
        try:
            db.create_all()
            print("Base de datos lista.")
            break
        except OperationalError:
            print("Esperando a la base de datos...")
            time.sleep(2)
    else:
        print("No se pudo conectar con la base de datos.")
        sys.exit(1)
