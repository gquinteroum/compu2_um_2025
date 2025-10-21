# ==========================================================
# Dockerfile: Python 3.14 free-threaded build (no GIL)
# Base: Debian Trixie
# ==========================================================
FROM debian:trixie-slim

# Evitar prompts interactivos y actualizar
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias para compilar CPython
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    curl \
    ca-certificates \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    tk-dev \
    uuid-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src

# Descargar el código fuente de Python 3.14
RUN wget https://www.python.org/ftp/python/3.14.0/Python-3.14.0.tgz && \
    tar -xf Python-3.14.0.tgz && \
    cd Python-3.14.0 && \
    ./configure --disable-gil --enable-optimizations --prefix=/usr/local && \
    make -j"$(nproc)" && \
    make install && \
    cd .. && rm -rf Python-3.14.0*

# Verificación
RUN python3 -c "import sys; import sysconfig; \
print('Python version:', sys.version); \
print('GIL enabled:', sys._is_gil_enabled()); \
print('Py_GIL_DISABLED:', sysconfig.get_config_var('Py_GIL_DISABLED'))"

WORKDIR /app
CMD ["python3"]
