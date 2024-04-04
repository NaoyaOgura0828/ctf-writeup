FROM python:3.10-slim

RUN apt update && apt install -y build-essential git curl

RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY ./src/pyproject.toml /app/
COPY ./src/poetry.lock /app/
RUN poetry install 

COPY ./src /app
COPY ./trial.png /app/

RUN adduser app && chown -R app /app