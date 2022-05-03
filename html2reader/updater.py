import datetime
import logging
import time
from pathlib import Path
from typing import Iterator

import dropbox
import dropbox.exceptions
from pony.orm import db_session, exists

from html2reader.article_fetcher import Article, PocketFetcher
from html2reader.converter import ConversionError, convert_to_fb2
from html2reader.db import DbArticle, DbAttempt

logger = logging.getLogger(__name__)


def filter_processed(articles: Iterator[Article]) -> Iterator[Article]:
    for article in articles:
        with db_session:
            if exists(e for e in DbArticle if e.pocket_id == article.id):  # type: ignore
                continue
        yield article


class UploadError(Exception):
    pass


def upload_to_dropbox(dropbox_client: dropbox.Dropbox, base_path: Path, local_file: Path) -> None:
    file_name = local_file.name
    with open(str(local_file), "rb") as file_output:
        try:
            dropbox_client.files_upload(file_output.read(), str((base_path / file_name).resolve()))
        except dropbox.exceptions.DropboxException as e:
            raise UploadError from e


class Updater:
    def __init__(
        self,
        pocket_fetcher: PocketFetcher,
        dropbox_client: dropbox.Dropbox,
        path: Path,
        interval: datetime.timedelta,
    ):
        self._pocket_fetcher = pocket_fetcher
        self._dropbox_client = dropbox_client
        self._path = path
        self._interval = interval

    def run(self) -> None:
        while True:
            try:
                for article in filter_processed(self._pocket_fetcher.fetch_all()):
                    with db_session:
                        if exists(e for e in DbAttempt if e.pocket_id == article.id):  # type: ignore
                            attempt = DbAttempt.get(pocket_id=article.id)
                            if attempt.number >= 3:
                                continue
                            attempt.number += 1
                        else:
                            DbAttempt(pocket_id=article.id, number=1)

                    logger.info("Processing article %s", article)
                    try:
                        local_file = convert_to_fb2(article=article)
                    except ConversionError:
                        logger.exception("Didn't convert article %s", article.id)
                        continue
                    try:
                        upload_to_dropbox(self._dropbox_client, base_path=self._path, local_file=local_file)
                    except UploadError:
                        logger.exception("Failed to upload article %s", article.id)
                        continue
                    with db_session:
                        DbArticle(pocket_id=article.id)
                    logger.info("article %s was processed", article)
            except Exception:
                logger.exception('Unexpected error')

            time.sleep(self._interval.total_seconds())
