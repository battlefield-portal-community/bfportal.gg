# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.11-buster as builder
RUN pip install poetry==1.5.1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /venv
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends git
RUN touch README.md

COPY ["pyproject.toml", "poetry.lock", "./"]
RUN poetry config installer.max-workers 10
RUN poetry install --without dev --no-root --no-cache

FROM node:latest as node_base
RUN echo "NODE Version:" && node --version
RUN echo "NPM Version:" && npm --version

FROM python:3.11-slim-buster as dev

WORKDIR /app
RUN useradd --create-home wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000
# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    curl \
&& rm -rf /var/lib/apt/lists/*
# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    USER="wagtail" \
    VIRTUAL_ENV=/venv/.venv

ENV PATH="${VIRTUAL_ENV}/bin:${PATH}:/home/wagtail/.local/bin"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}


COPY --chown=wagtail:wagtail --from=node_base /usr/local/bin /usr/local/bin
COPY --chown=wagtail:wagtail --from=node_base /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN chown -R wagtail:wagtail /app
COPY --chown=wagtail:wagtail ["package.json", "package-lock.json", "tailwind.config.js", "./"]
RUN npm install


# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail ./bfportal ./

FROM dev as final
USER wagtail
RUN npx tailwindcss -i ./bfportal/static/src/styles.css  -o ./bfportal/static/css/bfportal.css --minify
RUN python manage.py collectstatic --noinput --clear  -i static/src/*
