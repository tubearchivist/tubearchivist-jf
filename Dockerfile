FROM python:3.10.9-slim-bullseye
COPY . /jellyfin
WORKDIR jellyfin
RUN pip install -r requirements.txt
