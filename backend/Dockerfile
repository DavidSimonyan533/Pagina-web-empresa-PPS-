FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Convierte el script a formato Linux (evita fallos si Git lo guardó con saltos Windows)
# y crea un usuario sin privilegios de root.
RUN sed -i 's/\r$//' entrypoint.sh \
 && chmod +x entrypoint.sh \
 && useradd --system --uid 1001 appuser

USER appuser

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
