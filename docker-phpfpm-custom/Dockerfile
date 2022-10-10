
FROM php:7-fpm-alpine

# install all necesseary packages
RUN apk add --update --no-cache \
# php7-mysqli \
# php7-pdo \
# php7-pdo_mysql \
php7-mcrypt \
php7-mbstring \
php7-xml \
php7-openssl \
php7-json \
php7-phar \
php7-zip \
php7-dom \
php7-session \
# php7-memcached \
php7-zlib \
# curl \
# php7-curl \
# php7-zlib && \
# ln -s /usr/bin/php7 /usr/bin/php && \
# RUN ln -s /etc/php7/php.ini /etc/php7/conf.d/php.ini
# supervisor \
&& echo 'apk done'

RUN php -r "copy('http://getcomposer.org/installer', 'composer-setup.php');" && \
php composer-setup.php --install-dir=/usr/bin --filename=composer && \
php -r "unlink('composer-setup.php');" && \
echo 'composer installed'

RUN docker-php-ext-install \
mysqli pdo pdo_mysql \
&& docker-php-ext-enable pdo_mysql \
# && apk add --update bzip2-dev \
# && docker-php-ext-install bz2 \
&& echo 'docker-php-ext-install done'

# install memcached and geoip
# does we really need it in here?
ENV MEMCACHED_DEPS="zlib-dev libmemcached-dev cyrus-sasl-dev libzip-dev" \
	GEOIP_VERSION="1.1.1" \
	GEOIP_DEPS="geoip-dev "

RUN apk add --no-cache --update libmemcached-libs zlib geoip geoip-dev
RUN set -xe \
    && apk add --no-cache --update --virtual .phpize-deps $PHPIZE_DEPS \
    && apk add --no-cache --update --virtual .memcached-deps $MEMCACHED_DEPS \
    && apk add --no-cache --update --virtual .geoip-deps $GEOIP_DEPS \
    # && apk add --no-cache --update --virtual .geoip-deps $GEOIP_DEVS \
    && pecl install memcached zlib \
    && echo "extension=memcached.so" > /usr/local/etc/php/conf.d/20_memcached.ini \
    # geoip
    && curl -fsSL -o /tmp/ext-geoip.tgz https://pecl.php.net/get/geoip-${GEOIP_VERSION}.tgz \
	&& tar zxpf /tmp/ext-geoip.tgz -C /tmp \
    && cd /tmp/geoip-${GEOIP_VERSION} \
    && phpize && ./configure \
    && make -j${NPROC} && make install \
    && docker-php-ext-enable geoip \
		&& ( php -m | grep "^geoip$" ) \
	# eof: geoip
    # zip support
    # && docker-php-ext-configure zip --with-libzip \
    && docker-php-ext-install zip \
    # && docker-php-ext-enable zip \
    #eof zip suppoer
    && rm -rf /usr/share/php7 \
    && rm -rf /tmp/* \
    && apk del .memcached-deps .phpize-deps .geoip-deps

# create very simple php.ini file
RUN echo -e ";This sets the maximum amount of memory in bytes that a script is allowed to allocate\nmemory_limit = 1024M\n\n;The maximum size of an uploaded file.\nupload_max_filesize = 800M\n\n;Sets max size of post data allowed. This setting also affects file upload. To upload large files, this value must be larger than upload_max_filesize\npost_max_size = 800M\n\nmax_file_uploads = 200 ; Maxumim files to upload at once\r\nmax_execution_time = 600 ; Maximum execution time of each script, in seconds\nmax_input_time = 600 ; Maximum amount of time each script may spend parsing request data;\ndefault_socket_timeout = 600 ; Maximum socket wait\nmax_input_vars = 32000 ;This sets the maximum variables in request" > /usr/local/etc/php/php.ini
