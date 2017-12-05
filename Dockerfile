FROM python:2.7-alpine
LABEL maintainer="Chukwuerika Dike <chukwuerikadike@gmail.com>"

# Directory in container for all your project files
ENV PROJECT_DIR /lagos-bus-route
ENV APP_DIR /lagos-bus-route/lagos_bus_route
ENV DJANGO_SETTINGS_MODULE=lagos_bus_route.settings.production
RUN mkdir -p $APP_DIR
WORKDIR $APP_DIR


# Copy in your requirements file
ADD requirements.txt $PROJECT_DIR


# Install build deps, then run `pip install`, then remove unneeded build deps all in a
# single step. Correct the path to your production requirements file, if needed.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
    && pip install -r ../requirements.txt \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

# Copy your application code to the container (make sure you create a .dockerignore file)
# if any large files or directories should be excluded)
COPY /lagos_bus_route $APP_DIR


# gunicorn will listen on this port
EXPOSE 8000


# copy environment file into project dir
COPY ./env-prod $PROJECT_DIR


# COPY DATABASE JSON BACKUPS FOLDER INTO PROJECT DIR
COPY ./json_backups $PROJECT_DIR/json_backups


# Copy entrypoint script into the image
COPY ./entrypoint.sh $PROJECT_DIR
ENTRYPOINT ["/lagos-bus-route/entrypoint.sh"]
