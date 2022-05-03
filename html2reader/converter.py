import os
import re
import subprocess
import unicodedata
from pathlib import Path

import html2text
import requests
from lxml.html import fromstring
from requests import HTTPError, RequestException

from html2reader.article_fetcher import Article

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    pass


def slugify(value: str) -> str:
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def convert_to_fb2(article: Article) -> Path:
    headers = {"headers": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0"}
    try:
        response = requests.get(article.given_url, headers=headers)
        response.raise_for_status()
    except (HTTPError, RequestException, requests.ConnectionError) as e:
        raise ConversionError from e
    try:
        tree = fromstring(response.text)
    except Exception as e:
        raise ConversionError from e
    title = slugify(tree.findtext(".//title", str(article.id)))[:30]
    logger.info('Title: %s', title)
    text = html2text.html2text(response.text)
    local_path = Path("./results")
    os.makedirs(local_path, exist_ok=True)
    file_name = f"{title}.fb2"
    md_file = str((local_path / f"{title}.md").resolve())
    with open(md_file, 'w') as f:
        f.write(text)
    local_file = (local_path / file_name).resolve()
    try:
        result = subprocess.run(
            ['ebook-convert', md_file, str(local_file), f'--title={title}'],
            stdout=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            raise ConversionError(f'Calibre returned code {result.returncode}')
    except subprocess.SubprocessError as e:
        raise ConversionError from e
    return local_file
