FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y pandoc

RUN pip install requests html2text pypandoc lxml

ADD main.py .

ENTRYPOINT ["python", "main.py"]
