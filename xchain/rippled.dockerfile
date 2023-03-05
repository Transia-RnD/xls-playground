# docker build -t transia/rippled -f builder/docker/base.dockerfile . --build-arg DIR=issuing_chain
FROM gcr.io/metaxrplorer/dangell7-xchain-rippled:2 as base

WORKDIR /app

LABEL maintainer="dangell@transia.co"

RUN export LANGUAGE=C.UTF-8; export LANG=C.UTF-8; export LC_ALL=C.UTF-8; export DEBIAN_FRONTEND=noninteractive

ARG DIR
ENV DIR $DIR

COPY config/$DIR /config
COPY entrypoint /entrypoint.sh

RUN chmod +x /entrypoint.sh && \
    echo '#!/bin/bash' > /usr/bin/server_info && echo '/entrypoint.sh server_info' >> /usr/bin/server_info && \
    chmod +x /usr/bin/server_info

RUN export DOCKER_BUILDKIT=1

FROM base AS locking
RUN echo "BUILDING LOCKING RIPPLED"
EXPOSE 5005 6006 6005 51235
ENTRYPOINT [ "/entrypoint.sh", "--start", "-a" ]

FROM base AS issuing
RUN echo "BUILDING ISSUING RIPPLED"
EXPOSE 80 443 5006 6007 6008 51236
ENTRYPOINT [ "/entrypoint.sh", "--start", "-a" ]
