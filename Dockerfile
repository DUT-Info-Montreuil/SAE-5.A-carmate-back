FROM python:3-slim AS builder

ARG API_NAME
ARG API_PORT
ARG API_MODE
ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PWD
ARG POSTGRES_HOST
ARG POSTGRES_PORT

WORKDIR /app
COPY ./test test
COPY ./src src

RUN apt-get update \
    && apt-get install -y \
        libpq-dev \
        python3-dev \
        wget \
        # patch1f dependence
        autoconf \
        build-essential

RUN python3 -m pip install -r src/requirements.txt \
    && python3 -m pip install \
        pyinstaller \
        staticx

# staticx dependencies
RUN cd / \
    && wget https://github.com/NixOS/patchelf/archive/0.10.tar.gz\
    && tar xzf 0.10.tar.gz \
    && cd patchelf-0.10 \
    && ./bootstrap.sh \
    && ./configure \
    && make \
    && make install

RUN cd /app \
    && PYTHONPATH=./ pyinstaller -F -y src/main.py \
    && cd ./dist && staticx main main_app

# main_app need to have a "tmp" directory to work
RUN mkdir tmp

FROM scratch

COPY --from=builder --chmod=777 /app/dist/main_app /main_app
COPY --from=builder --chmod=777 /app/tmp /tmp

EXPOSE 5000
ENTRYPOINT [ "/main_app" ]
