# Davem Cyber Consulting

Web de una consultora de ciberseguridad (auditoría interna, ISO 27001, ENS, NIS2 y otros servicios), con registro de usuarios, área de cliente y solicitud de auditorías. Es un **proyecto académico**: la empresa es ficticia y la web se ejecuta en local.

**Tecnologías:** Flask (Python 3.12), PostgreSQL 16, Docker Compose.

## Arranque rápido

Necesitas [Docker](https://docs.docker.com/get-docker/) con Docker Compose.

```bash
cp .env.example .env        # y cambia SECRET_KEY y POSTGRES_PASSWORD
docker compose up --build
```

Abre <http://localhost:8000>. Para parar: `Ctrl+C`; para borrar también los datos: `docker compose down -v`.

Para generar una `SECRET_KEY` válida:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Páginas

| Ruta | Descripción |
|---|---|
| `/` | Portada |
| `/servicios` | Catálogo de servicios |
| `/sobre-nosotros`, `/blog`, `/contacto`, `/privacidad` | Páginas informativas y formulario de contacto |
| `/registro`, `/login` | Alta y acceso de usuarios |
| `/cliente/` | Área de cliente (requiere sesión) |
| `/cliente/solicitar-auditoria` | Formulario de solicitud (requiere sesión) |
| `/health` | Comprobación de estado |

## Estructura

```
├── docker-compose.yml      # servicios web + db
├── .env.example            # plantilla de configuración (copiar a .env)
└── backend/
    ├── Dockerfile
    ├── entrypoint.sh       # crea las tablas y arranca gunicorn
    ├── init_db.py
    ├── requirements.txt
    ├── app/
    │   ├── __init__.py     # fábrica de la app, cabeceras de seguridad, errores
    │   ├── config.py       # configuración desde variables de entorno
    │   ├── models.py       # User, AuditRequest, ContactMessage
    │   ├── security.py     # hash de contraseñas (Argon2) y redirecciones seguras
    │   ├── forms.py        # formularios y validaciones
    │   ├── main.py         # páginas públicas
    │   ├── auth.py         # registro, login y logout
    │   ├── cliente.py      # área de cliente y solicitudes
    │   ├── content.py      # servicios, proceso y artículos del blog
    │   ├── templates/
    │   └── static/css/
    └── tests/
```

## Medidas de seguridad incluidas

- Contraseñas guardadas con **Argon2** (nunca en claro) y mínimo de 12 caracteres.
- Consultas a la base de datos mediante **SQLAlchemy** (parametrizadas).
- **Protección CSRF** en todos los formularios, incluido el cierre de sesión (solo por POST).
- **Límite de intentos** en login, registro y contacto (5 por minuto).
- Mismo mensaje y tiempo de respuesta para correo inexistente y contraseña incorrecta.
- Cookies de sesión `HttpOnly` y `SameSite=Lax`; `Secure` activable con `COOKIE_SECURE=true`; sesión limitada a 2 horas.
- Redirección `next` restringida a rutas internas.
- Cabeceras: `Content-Security-Policy` estricta (sin scripts ni estilos en línea), `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` y `Permissions-Policy`.
- Páginas de sesión y de cliente con `Cache-Control: no-store`.
- Tamaño máximo de petición de 64 KB.
- Contenedor sin root y base de datos **sin puertos publicados** en el equipo.
- Secretos fuera del código (`.env` está en `.gitignore`).

## Limitaciones conocidas (mejoras futuras)

- No hay verificación del correo electrónico ni recuperación de contraseña.
- No hay doble factor de autenticación.
- El servicio funciona por HTTP en local; en un despliegue real hace falta HTTPS (por ejemplo con un proxy inverso) y `COOKIE_SECURE=true`.
- El limitador guarda los contadores en memoria (por eso se usa un solo proceso de gunicorn); en producción conviene Redis.
- No hay panel de administración para gestionar solicitudes y mensajes.
- La política de privacidad y los textos son de ejemplo.

## Pruebas

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Cambiar el nombre o el contenido

- Nombre de la marca: plantillas `base.html`, `index.html`, `sobre.html` y `privacidad.html`.
- Servicios, proceso de trabajo y artículos: `backend/app/content.py`.
- Colores y tipografías: variables al principio de `backend/app/static/css/style.css`.
