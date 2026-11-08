#!/bin/sh
set -e
# Crea las tablas (espera a que la base de datos responda) y arranca el servidor.
python init_db.py
# 1 worker con hilos: el limitador de intentos guarda sus contadores en memoria.
exec gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 4 "app:create_app()"
