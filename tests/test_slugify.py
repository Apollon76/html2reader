import pytest

from html2reader.converter import slugify


@pytest.mark.parametrize(('text', 'expected'), [('Привет. Как дела?', 'привет-как-дела')])
def test_slugify(text: str, expected: str):
    assert slugify(text) == expected
