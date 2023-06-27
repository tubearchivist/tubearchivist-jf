FROM python:3.10.9-slim-bullseye
RUN apt-get update && apt-get install -y --no-install-recommends \
    git
RUN git clone https://github.com/tubearchivist/jellyfin
WORKDIR jellyfin
RUN pip install -r requirements.txt
