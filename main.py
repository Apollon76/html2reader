import datetime
import logging
from pathlib import Path

import dropbox
from pocket import Pocket

from html2reader.settings import PocketSettings, DropboxSettings
from html2reader.updater import Updater
from html2reader.article_fetcher import PocketFetcher
from html2reader.db import db

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    db.bind(provider="sqlite", filename="database/database.sqlite", create_db=True)
    db.generate_mapping(create_tables=True)

    # response = requests.post(url='https://getpocket.com/v3/oauth/request', json={'consumer_key': consumer_key, 'redirect_uri': 'http://example.com'})
    # code = response.content.decode()[len('code='):]
    # print(code)
    # print(f'https://getpocket.com/auth/authorize?request_token={code}&redirect_uri=http://example.com')
    # auth_response = requests.post(url='https://getpocket.com/v3/oauth/authorize', json={'consumer_key': consumer_key, 'code': code})
    # print(auth_response.content)
    pocket_settings = PocketSettings()
    pocket_client = Pocket(
        consumer_key=pocket_settings.consumer_key,
        access_token=pocket_settings.access_token,
    )
    dropbox_settings = DropboxSettings()
    dropbox_client = dropbox.Dropbox(dropbox_settings.access_token)
    try:
        Updater(
            pocket_fetcher=PocketFetcher(pocket_client=pocket_client),
            dropbox_client=dropbox_client,
            path=Path(dropbox_settings.file_path),
            interval=datetime.timedelta(seconds=30),
        ).run()
    except Exception as e:
        file_handler = logging.FileHandler('logs/err.log', 'a')
        logger.addHandler(file_handler)
        logger.exception(e)
        raise


if __name__ == "__main__":
    main()
