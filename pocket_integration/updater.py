import datetime
import logging
import os
import re
import subprocess
import time
import unicodedata
from pathlib import Path

import dropbox
import dropbox.exceptions
import html2text
import requests
from lxml.html import fromstring
from pocket import Pocket, PocketException
from pony.orm import Database, Required, PrimaryKey, db_session, exists
from pydantic import BaseModel, Field
from requests import HTTPError, RequestException

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
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


class Article(BaseModel):
    id: str = Field(alias="item_id")
    resolved_url: str
    given_url: str


db = Database()


class DbArticle(db.Entity):
    id = PrimaryKey(int, auto=True)
    pocket_id = Required(str, unique=True, index=True)


class DbAttempt(db.Entity):
    id = PrimaryKey(int, auto=True)
    pocket_id = Required(str, unique=True, index=True)
    number = Required(int, sql_default=0)


class Updater:
    def __init__(
        self,
        pocket_client: Pocket,
        dropbox_client: dropbox.Dropbox,
        path: Path,
        interval: datetime.timedelta,
    ):
        self._pocket_client = pocket_client
        self._dropbox_client = dropbox_client
        self._path = path
        self._interval = interval

    def run(self) -> None:
        while True:
            offset = 0
            while True:
                try:
                    data = self._pocket_client.retrieve(offset=offset, count=10)["list"]
                except PocketException as e:
                    logger.exception(e)
                    break
                if not data:
                    break
                for _, value in data.items():
                    article = Article.parse_obj(value)
                    with db_session:
                        if exists(e for e in DbArticle if e.pocket_id == article.id):
                            continue
                    logger.info("Processing article %s", article)
                    try:
                        with db_session:
                            if exists(
                                e for e in DbAttempt if e.pocket_id == article.id
                            ):
                                attempt = DbAttempt.get(pocket_id=article.id)
                                if attempt.number >= 3:
                                    continue
                                attempt.number += 1
                            else:
                                DbAttempt(pocket_id=article.id, number=1)
                        self._process(article)
                        with db_session:
                            DbArticle(pocket_id=article.id)
                        logger.info("article=%s was processed", article)
                    except ConversionError as e:
                        logger.exception(e)
                offset += len(data)
            time.sleep(self._interval.total_seconds())

    def _process(self, article: Article) -> None:
        headers = {
            "headers": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0"
        }
        try:
            response = requests.get(article.given_url, headers=headers)
            response.raise_for_status()
        except (HTTPError, RequestException, requests.ConnectionError) as e:
            raise ConversionError from e
        tree = fromstring(response.content)
        title = slugify(tree.findtext(".//title", str(article.id)))[:30]
        logger.info('Title: %s', title)
        text = html2text.html2text(response.text)
        local_path = Path("./results")
        os.makedirs(local_path, exist_ok=True)
        file_name = f"{title}.fb2"
        md_file = str((local_path / f"{title}.md").resolve())
        with open(md_file, 'w') as f:
            f.write(text)
        local_file = str((local_path / file_name).resolve())
        try:
            result = subprocess.run(
                ['ebook-convert', md_file, local_file, f'--title={title}'],
                stdout=subprocess.DEVNULL,
            )
            if result.returncode != 0:
                raise ConversionError(f'Calibre returned code {result.returncode}')
        except subprocess.SubprocessError as e:
            raise ConversionError from e
        with open(local_file, "rb") as f:
            try:
                self._dropbox_client.files_upload(
                    f.read(), str((self._path / file_name).resolve())
                )
            except dropbox.exceptions.DropboxException as e:
                raise ConversionError from e
