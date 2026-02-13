FROM python:3.13.11-slim-trixie

# create the app directory
RUN mkdir /app
WORKDIR /app

# copy source files
COPY src/ ./src/
COPY main.py ./main.py

# update
RUN apt-get update
# RUN apt-get install -y --no-install-recommends ffmpeg
# RUN rm -rf /var/lib/apt/lists/*

# install pydependencies
RUN pip install --no-cache-dir -r src/requirements.txt

CMD ["python", "main.py"]