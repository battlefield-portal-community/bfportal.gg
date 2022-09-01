# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.10-slim-buster

# Add user that will be used in the container.
RUN useradd --create-home wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="${PATH}:/home/wagtail/.local/bin" \
    USER="wagtail"

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    curl \
    wget \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    software-properties-common \
    zip \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

RUN wget -q https://github.com/Schniz/fnm/releases/latest/download/fnm-linux.zip \
    && unzip -j fnm-linux.zip \
    && chmod +x fnm \
    && mv fnm /usr/local/bin/

RUN fnm install v18.8.0

# Install the application server.
RUN pip install "gunicorn==20.0.4"

# Install the project requirements.
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown wagtail:wagtail /app

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail

RUN python manage.py tailwind install --no-input;
RUN python manage.py tailwind build --no-input
RUN python manage.py collectstatic --noinput --clear
