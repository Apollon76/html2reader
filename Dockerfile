FROM python:3.9-slim

WORKDIR /app
VOLUME /app

RUN apt-get update && apt-get install -y calibre

RUN pip install requests html2text lxml dropbox pocket-api
RUN pip install pydantic
RUN pip install pony

ADD main.py .
ADD html2reader/* html2reader/

RUN mkdir results
RUN mkdir database

ENTRYPOINT ["python", "main.py"]
# ENTRYPOINT ["/bin/bash"]
