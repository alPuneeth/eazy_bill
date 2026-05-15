# -- Stage 1: builder --
# Installs all dependencies inculding build tools 
# Never ships to production
FROM python:3.13-slim AS builder

WORKDIR /app

# gcc and libpq-dev are needed to compile psycopg's C extension
# --no-install-recommends skips optional extras - keeps layer lean
# rm -rf in same RUN = apt cache never committed to this layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first - layer cache optimisation
# pip install only reruns when requirements.txt changes
COPY requirements.txt requirements-dev.txt ./

# Install dependencies into custom directory
# /install becomes a self-contained dependency bundle
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Dev deps into separate /install-dev
RUN pip install --no-cache-dir --prefix=/install-dev -r requirements-dev.txt


# -- Stage 2: final --
# Clean slate - gcc, libpq-dev, pip cache all left behind in builder
# Clean runtime image without compiler/build tools
FROM python:3.13-slim AS final

# Flush logs immediately - critical for docker logs on crash
# skip .pyc files - useless in ephemeral containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy ONLY installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Make start.sh(start up script) executable inside the image
RUN chmod +x start.sh

# Healthcheck - uses existing /db_check endpoint
# start_period gives migrations time to complete before checks begin
HEALTHCHECK \
    --interval=30s \
    --timeout=30s \
    --start-period=20s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/db_check')" || exit 1

EXPOSE 8000

# bash start.sh runs migrations then starts uvicorn
# exec in start.sh ensures uvicorn becomes PID 1
CMD ["bash", "start.sh"]


# -- Stage 3: test --
# Builds on top of final - adds dev packages and test files
FROM final AS test

# Add dev packages on top of production image
COPY --from=builder /install-dev /usr/local

# Copy test files
COPY tests/ tests/

# Default command for test stage
CMD ["pytest", "tests/", "-v"]
