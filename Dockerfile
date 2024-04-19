FROM python:3.11.8-slim-bookworm
ARG INSTALL_DEBUG
ENV PYTHONUNBUFFERED 1
ENV PATH=/root/.local/bin:$PATH

# install debug tools for testing environment
RUN if [ "$INSTALL_DEBUG" ] ; then \
        apt-get -y update && apt-get -y install --no-install-recommends \
        vim htop bmon net-tools iputils-ping procps curl \
        && pip install ipython \
    ; fi

# install requirements
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY app /app
WORKDIR app

VOLUME /youtube

CMD ["python", "server.py"]
