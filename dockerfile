FROM python:3.13.11-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# main directory
RUN mkdir /app && chown -R appuser:appuser /app

WORKDIR /app

# copy src and change owner
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser main.py ./main.py

# update packages and dependencies (as root)
RUN apt-get update
RUN uv pip install -r src/requirements.txt --system

# change user
USER appuser

CMD ["python", "main.py"]