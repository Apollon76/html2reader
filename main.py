import html2text
import requests
from pathlib import Path
import sys
import os
from lxml.html import fromstring
import unicodedata
import re
import pypandoc


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    value = unicodedata.normalize('NFKC', value)
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def main():
    url = sys.argv[1]
    headers = {'headers':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    tree = fromstring(response.content)
    title = slugify(tree.findtext('.//title'))
    text = html2text.html2text(response.text)
    path = Path('./results')
    os.makedirs(path, exist_ok=True)
    pypandoc.convert_text(text, 'fb2', format='md', outputfile=str((path / f'{title}.fb2').resolve()))


if __name__ == '__main__':
    main()

