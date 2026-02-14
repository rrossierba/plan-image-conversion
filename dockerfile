FROM python:3.13.11-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# these will be overwritten from the .env file
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USERNAME=user
RUN groupadd -g ${GROUP_ID} ${USERNAME} && \
    useradd -u ${USER_ID} -g ${USERNAME} -m -s /bin/bash ${USERNAME}

# create working directory
RUN mkdir -p /app /result && \
    chown -R ${USERNAME}:${USERNAME} /app /result
WORKDIR /app

# copy files
COPY --chown=${USERNAME}:${USERNAME} src/ ./src/
COPY --chown=${USERNAME}:${USERNAME} main.py ./main.py

# update and install dependencies
RUN apt-get update
RUN uv pip install -r src/requirements.txt --system

# change user
USER ${USERNAME}

CMD ["python", "main.py"]