FROM python:3.13.11-slim

# Instalamos uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

# Instalamos dependencias primero para aprovechar el cache de capas
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

# Copiamos ambos scripts al contenedor
COPY green_tripdata_parquet.py zones-dataset.py ./

# No usamos ENTRYPOINT fijo para poder elegir qué script correr al lanzar el contenedor
# Pero dejamos un comando por defecto por si acaso
CMD ["uv", "run", "green_tripdata_parquet.py"]