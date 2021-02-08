FROM python:3.9-slim

WORKDIR /app
VOLUME /app

RUN apt-get update && apt-get install -y pandoc

RUN pip install requests html2text pypandoc lxml

ADD main.py .
ADD pocket_integration pocket_integration

RUN mkdir results

ENTRYPOINT ["python", "main.py"]
