FROM python:3.7-alpine3.10

RUN apk add --no-cache mariadb-connector-c-dev;\
    apk add --no-cache --virtual .build-deps \
        build-base \
        python3-dev \
        mariadb-dev; \
    pip3 install --no-cache-dir mysqlclient && \
    pip3 install --no-cache-dir PySocks && \
    pip3 install --no-cache-dir dnspython && \
    pip3 install --no-cache-dir yattag && \
    pip3 install --no-cache-dir supervisor && \
    pip3 install --no-cache-dir redis && \
    pip3 install --no-cache-dir python-dotenv && \
    pip3 install --no-cache-dir beautifulsoup4 && \
    pip3 install --no-cache-dir langdetect && \
    pip3 install --no-cache-dir murmurhash3 && \
    apk del .build-deps && \
    echo 'done'

# https://stackoverflow.com/questions/58738920/running-geckodriver-in-an-alpine-docker-container
RUN pip3 install --no-cache-dir sqlalchemy sqlalchemy_utils pymysql
RUN pip3 install --no-cache-dir requests
RUN pip3 install --no-cache-dir pefile

# This is only for web grabber actually, so i guess i need another image for that
RUN pip3 install --no-cache-dir selenium
RUN pip3 install --no-cache-dir pyvirtualdisplay
RUN pip3 install --no-cache-dir nest_asyncio

RUN apk add --no-cache curl xvfb xdpyinfo

# Get all the prereqs
# RUN wget --no-check-certificate -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub
# RUN wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-2.30-r0.apk
# RUN wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-bin-2.30-r0.apk
# RUN apk add glibc-2.30-r0.apk
# RUN apk add glibc-bin-2.30-r0.apk
COPY sgerrand.rsa.pub /etc/apk/keys/sgerrand.rsa.pub
COPY glibc-2.30-r0.apk glibc-2.30-r0.apk
COPY glibc-bin-2.30-r0.apk glibc-bin-2.30-r0.apk
RUN apk add glibc-2.30-r0.apk
RUN apk add glibc-bin-2.30-r0.apk


# And of course we need Firefox if we actually want to *use* GeckoDriver
RUN apk add --no-cache firefox-esr=60.9.0-r0

# Then install GeckoDriver
# RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
COPY geckodriver-v0.26.0-linux64.tar.gz geckodriver-v0.26.0-linux64.tar.gz
RUN tar -zxf geckodriver-v0.26.0-linux64.tar.gz -C /usr/bin
RUN geckodriver --version

RUN apk add --no-cache --virtual .build-deps2 \
        build-base; \
    apk add --no-cache libxml2-dev && \
    apk add --no-cache libxslt-dev && \
    apk add --no-cache libxslt && \
    pip3 install --no-cache-dir lxml && \
    apk del .build-deps2 && \
    echo 'done2'

