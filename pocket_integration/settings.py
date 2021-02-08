from pydantic import BaseSettings


class PocketSettings(BaseSettings):
    consumer_key: str
    access_token: str

    class Config:
        env_prefix = 'POCKET_'


class DropboxSettings(BaseSettings):
    access_token: str
    file_path: str

    class Config:
        env_prefix = 'DROPBOX_'
