from typing import Iterator

from pocket import Pocket
from pydantic import BaseModel, Field


class Article(BaseModel):
    id: str = Field(alias="item_id")
    given_url: str


class PocketFetcher:
    def __init__(
        self,
        pocket_client: Pocket,
    ):
        self._pocket_client = pocket_client

    def fetch_all(self) -> Iterator[Article]:
        offset = 0
        while True:
            data = self._pocket_client.retrieve(offset=offset, count=10)["list"]
            if not data:
                break
            for _, value in data.items():
                yield Article.parse_obj(value)
            offset += len(data)
