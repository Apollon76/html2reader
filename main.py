import datetime
import logging
from pathlib import Path

import dropbox
from pocket import Pocket

from pocket_integration.settings import PocketSettings, DropboxSettings
from pocket_integration.updater import db, Updater

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    db.bind(provider="sqlite", filename="database/database.sqlite", create_db=True)
    db.generate_mapping(create_tables=True)
    # with db_session:
    #     for e in select(e for e in DbArticle):
    #         print(e.pocket_id)
    # exit(0)

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
            pocket_client,
            dropbox_client=dropbox_client,
            path=Path(dropbox_settings.file_path),
            interval=datetime.timedelta(seconds=30),
        ).run()
    except Exception as e:
        file_handler = logging.FileHandler('err.log', 'a')
        logger.addHandler(file_handler)
        logger.exception(e)
        raise


if __name__ == "__main__":
    main()
