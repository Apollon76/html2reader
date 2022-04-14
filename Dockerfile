FROM python:3.9-slim

WORKDIR /app
VOLUME /app

RUN apt-get update && apt-get install -y calibre

RUN pip install --no-cache -U pip
RUN pip install --no-cache poetry

COPY pyproject.toml .
COPY poetry.lock .

RUN mkdir html2reader && \
  touch html2reader/__init__.py && \
  poetry config virtualenvs.create false && \
  poetry install --no-dev --no-ansi --no-interaction && \
  pip uninstall --yes poetry

ADD main.py .
ADD html2reader/* html2reader/

RUN mkdir results
RUN mkdir database

ENTRYPOINT ["python", "main.py"]
# ENTRYPOINT ["/bin/bash"]
