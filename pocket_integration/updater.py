import logging
import os
import re
import time
import unicodedata
from pathlib import Path

import html2text
import pypandoc
import requests
from pocket import Pocket, PocketException
from pydantic import BaseModel, Field
from lxml.html import fromstring
from requests import HTTPError


logger = logging.getLogger(__name__)

class ConversionError(Exception):
    pass


def slugify(value: str):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = unicodedata.normalize('NFKC', value)
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


class Article(BaseModel):
    id: str = Field(alias='item_id')
    resolved_url: str
    given_url: str

def process(article: Article):
    headers = {'headers': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}
    try:
        response = requests.get(article.given_url, headers=headers)
        response.raise_for_status()
    except HTTPError as e:
        raise ConversionError from e
    tree = fromstring(response.content)
    title = slugify(tree.findtext('.//title'))
    text = html2text.html2text(response.text)
    path = Path('./results')
    os.makedirs(path, exist_ok=True)
    try:
        pypandoc.convert_text(text, 'fb2', format='md', outputfile=str((path / f'{title}.fb2').resolve()))
    except RuntimeError as e:
        raise ConversionError from e


class Updater:
    def __init__(self, client: Pocket):
        self._client = client
        self._processed = set()

    def run(self) -> None:
        while True:
            offset = 0
            while True:
                try:
                    data = self._client.retrieve(offset=offset, count=10)['list']
                except PocketException as e:
                    logger.exception(e)
                    break
                if not data:
                    break
                for _, value in data.items():
                    article = Article.parse_obj(value)
                    if article.id in self._processed:
                        continue
                    logger.info('Processing article %s', article)
                    try:
                        process(article)
                        self._processed.add(article.id)
                        logger.info('article=%s was processed', article)
                    except ConversionError as e:
                        logger.exception(e)
                offset += len(data)
            time.sleep(10)


if __name__ == '__main__':
    consumer_key = os.environ['CONSUMER_KEY']
    access_token = os.environ['ACCESS_TOKEN']

    # response = requests.post(url='https://getpocket.com/v3/oauth/request', json={'consumer_key': consumer_key, 'redirect_uri': 'http://example.com'})
    # code = response.content.decode()[len('code='):]
    # print(code)
    # print(f'https://getpocket.com/auth/authorize?request_token={code}&redirect_uri=http://example.com')
    # auth_response = requests.post(url='https://getpocket.com/v3/oauth/authorize', json={'consumer_key': consumer_key, 'code': code})
    # print(auth_response.content)
    client = Pocket(
        consumer_key=consumer_key,
        access_token=access_token
    )
    Updater(client).run()