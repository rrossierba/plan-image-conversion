FROM python:3.13.11-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app /result
WORKDIR /app

COPY src/ ./src/
COPY main.py ./main.py

RUN apt-get update
RUN apt-get install -y --no-install-recommends ffmpeg 
RUN uv pip install -r src/requirements.txt --system

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
ENV CONFIG_FILE=/app/files/config.json
CMD ["python", "main.py"]