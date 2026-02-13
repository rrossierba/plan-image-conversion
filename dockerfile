FROM python:3.13.11-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# create the app directory
RUN mkdir /app
WORKDIR /app

# copy source files
COPY src/ ./src/
COPY main.py ./main.py

# update
RUN apt-get update

# install pydependencies
RUN uv pip install -r src/requirements.txt --system

CMD ["python", "main.py"]