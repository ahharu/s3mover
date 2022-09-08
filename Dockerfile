FROM alpine:3.8
ADD . /app
WORKDIR /app
########################################################################################################################
# Install Dockerize
########################################################################################################################

ENV DOCKERIZE_VERSION=v0.6.1
RUN apk add --no-cache python3 python3-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk --update add --no-cache gcc freetype-dev libpng-dev

RUN apk add --no-cache --virtual .build-deps \
    g++

RUN apk add --no-cache --update gcc wget alpine-sdk wget libffi-dev python3-tkinter build-base \
    && wget -O /tmp/dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-${DOCKERIZE_VERSION}.tar.gz \
    && tar -C /usr/local/bin -xzvf /tmp/dockerize.tar.gz \
    && rm -rf /var/cache/apk/* /tmp/*

########################################################################################################################
# Add Wait-for script
########################################################################################################################
ADD wait-for.sh .

########################################################################################################################
# Install Alembic and Psycopg2 and MySQL
########################################################################################################################

ADD alembic.ini.tmpl .

RUN apk update \
  && apk add --virtual build-deps gcc python3-dev mariadb-dev mysql-client \
  && rm -rf /var/cache/apk/* /tmp/*

RUN pip install -r requirements.txt
RUN apk del .build-deps
CMD python ./s3mover.py
