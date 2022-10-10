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

RUN pip3 install --no-cache-dir sqlalchemy sqlalchemy_utils pymysql
RUN pip3 install --no-cache-dir requests
RUN pip3 install --no-cache-dir pefile

RUN apk add --no-cache --virtual .build-deps2 \
        build-base; \
    apk add --no-cache libxml2-dev && \
    apk add --no-cache libxslt-dev && \
    apk add --no-cache libxslt && \
    pip3 install --no-cache-dir lxml && \
    apk del .build-deps2 && \
    echo 'done2'

# RUN apk add --no-cache build-base; \
#     apk add --no-cache libxml2-dev && \
#     apk add --no-cache libxslt-dev && \
#     pip3 install --no-cache-dir lxml && \
#     echo 'done2'

# attempt to control network bandwidth
# https://www.iplocation.net/traffic-control

# RUN apk add --no-cache iproute2;\
#     wget https://raw.githubusercontent.com/magnific0/wondershaper/master/wondershaper;\
#     chmod +x wondershaper;\
#     sed -i "1s/.*/\#\!\/bin\/sh/" wondershaper

# COPY ./shaping /etc/init.d/shaping

# RUN chmod +x /etc/init.d/shaping
