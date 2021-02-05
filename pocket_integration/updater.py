import requests
from pocket import Pocket, PocketException


class Updater:
    def __init__(self, client: Pocket):
        self._client = client

    def run(self) -> None:
        while True:
            try:
                print(self._client.retrieve(offset=0, count=10))
            except PocketException as e:
                print(e.message)
            # articles = self._client.retrieve(offset=0, count=10)
            # print(type(articles))
            # print(articles)


if __name__ == '__main__':
    response = requests.post(url='https://getpocket.com/v3/oauth/request', data={'consumer_key': '95679-3d84afce9452f136dc0ca00e', 'redirect_uri': 'http://example.com'})
    code = response.content.decode()#[len('code='):]
    print(code)
    client = Pocket(
        consumer_key='95679-3d84afce9452f136dc0ca00e',
        access_token=code
    )
    Updater(client).run()