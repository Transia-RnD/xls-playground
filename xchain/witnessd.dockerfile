# docker build -t transia/witness -f witnessd.dockerfile . --build-arg DIR=witness0 --build-arg PORT=6010
# docker run --rm -it transia/witness
FROM gcr.io/metaxrplorer/dangell7-witness-witness:latest as base

# WITNESS (BUILD) IS IN /app/witness
WORKDIR /app
USER root

LABEL maintainer="dangell@transia.co"

RUN export LANGUAGE=C.UTF-8; export LANG=C.UTF-8; export LC_ALL=C.UTF-8; export DEBIAN_FRONTEND=noninteractive

ARG DIR
ENV DIR $DIR
ARG PORT
ENV PORT $PORT

COPY config/$DIR /config

EXPOSE $PORT

CMD [ "./witness", "--config", "/config/witness.json", "--verbose" ]
