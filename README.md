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
| `/tarifas` | Packs, calculadora de presupuesto y precios por servicio |
| `/sobre-nosotros`, `/blog`, `/contacto`, `/preguntas-frecuentes` | Páginas informativas y formulario de contacto |
| `/aviso-legal`, `/privacidad`, `/cookies` | Páginas legales (LSSI-CE y RGPD) |
| `/registro`, `/login` | Alta y acceso de usuarios |
| `/cliente/` | Área de cliente (requiere sesión) |
| `/cliente/solicitar-auditoria` | Formulario de solicitud (requiere sesión) |
| `/admin/` | Panel de administración (admin con doble factor) |
| `/admin/seguridad` | Registro de eventos de seguridad |
| `/admin/doble-factor` | Activación del doble factor |
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

## Diseño y experiencia

- **Sección de radar de vigilancia** en la portada (`static/js/radar.js`): un barrido animado en canvas que ilumina incidencias, con cifras que cuentan hacia arriba al aparecer.
- **Buscador de servicios** que filtra la lista al escribir (ignora mayúsculas y tildes).
- **Tiempo de lectura** estimado en el blog.
- **Cabeceras animadas (aurora)** en todas las páginas interiores: degradados en movimiento y una rejilla de puntos, en CSS puro.
- **Barra de progreso de scroll**, botón de **volver arriba** y animación de entrada en cada página.
- **Foco de luz que sigue al cursor** en las tarjetas (`static/js/effects.js`) y **botones magnéticos**.
- **Medidor de fuerza de la contraseña** en el registro, en tiempo real.
- **Barra de progreso de lectura** en los artículos del blog.
- **Página de error 404** con número animado.
- **Banner de cookies conforme a la AEPD** (`static/js/cookies.js`): aceptar todas, rechazar (igual de visible) o configurar por categorías, con panel de preferencias reabrible desde el pie. Nada opcional se activa sin consentimiento y la elección se guarda en el navegador. La web no usa cookies de terceros reales.
- **Portada con fondo WebGL propio** (`static/js/hero.js`): red de nodos animada que reacciona al ratón. Se pausa cuando no está a la vista y, si el usuario prefiere movimiento reducido, se dibuja estática. Sin vídeos ni recursos externos.
- **Autodiagnóstico** en la portada (`static/js/diagnostico.js`): recomienda servicios según las respuestas. No envía datos: se calcula en el navegador.
- **Tipografías Inter y Lora alojadas en la propia web** (`static/fonts/`, licencia SIL OFL 1.1), sin Google Fonts.
- Escenarios de ejemplo, línea de tiempo con plazos, tarifas con calculadora e iconos e ilustraciones SVG propios.
- Todo funciona con la `Content-Security-Policy` estricta: ningún script, estilo, fuente ni imagen de terceros.

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
- **Doble factor (TOTP, RFC 6238)** obligatorio para el panel de administración; los códigos no se pueden reutilizar.
- **Registro de eventos de seguridad**: logins correctos y fallidos, bloqueos por exceso de intentos, accesos denegados, códigos 2FA erróneos y cambios hechos por el administrador, con IP y ruta.
- Cuentas de administrador solo creables desde la terminal del servidor, nunca desde la web.
- Secretos fuera del código (`.env` está en `.gitignore`).

## Limitaciones conocidas (mejoras futuras)

- No hay verificación del correo electrónico ni recuperación de contraseña.
- El doble factor solo está disponible para administradores.
- El servicio funciona por HTTP en local; en un despliegue real hace falta HTTPS (por ejemplo con un proxy inverso) y `COOKIE_SECURE=true`.
- El limitador guarda los contadores en memoria (por eso se usa un solo proceso de gunicorn); en producción conviene Redis.
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

## Panel de administración

Las cuentas de administrador no se crean desde la web. Se crean desde la terminal, con una contraseña que tú eliges en el momento:

```bash
docker compose exec -it web flask create-admin
```

Te pedirá correo, nombre y contraseña (mínimo 12 caracteres). Después entra con esa cuenta y pulsa **Administración** en la cabecera, o ve a `/admin`. La primera vez te pedirá activar el doble factor con una aplicación como Google Authenticator, Microsoft Authenticator o Aegis.

Si pierdes el móvil, desactiva el doble factor de una cuenta con:

```bash
docker compose exec -it web flask reset-2fa
``` Desde ahí puedes ver las solicitudes de auditoría, cambiar su estado, leer los mensajes de contacto y consultar los usuarios.

## Acceso desde la red local (clase)

La web se publica en el puerto 8000 de tu equipo. Tus compañeros pueden entrar con `http://IP_DEL_EQUIPO:8000` si están en la misma red y el equipo está en un perfil de red **Privado**. La IP se ve con `ipconfig`. Para permitir la conexión en Windows, ejecuta una vez en PowerShell como administrador:

```powershell
New-NetFirewallRule -DisplayName "Davem Web 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private
```

Mientras la web esté expuesta, la conexión es HTTP sin cifrar. Apaga el servicio con `docker compose down` cuando termines.

## Actualizar a una versión nueva

Al arrancar, `init_db.py` crea las tablas que falten y añade las columnas nuevas a las tablas existentes, así que no hace falta borrar la base de datos (`docker compose down -v`) al actualizar el código. Basta con:

```bash
docker compose up --build
```
