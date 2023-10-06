FROM python:3.8

WORKDIR "/usr/src/app/"

RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list
RUN apt update
RUN apt install -y --no-install-recommends firefox

COPY poetry.lock ./
COPY pyproject.toml ./
RUN pip install poetry
RUN poetry install