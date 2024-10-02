import logging

from bs4 import BeautifulSoup
from goose3 import Goose

from .const import HTML_ATTR_IGNORE, HTML_TAG_IGNORE


def clean_html(
    html: str,
    *,
    html_tag_ignore: list[str] = HTML_TAG_IGNORE,
    html_attr_ignore: list[str] = HTML_ATTR_IGNORE,
) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")

    for el in soup(html_tag_ignore):
        el.decompose()

    for el in soup.find_all(True):
        for attr in html_attr_ignore:
            del el[attr]

    output_html = str(soup)

    logging.info(
        f"HTML cleaned. Size reduced to {round(len(output_html) / len(html) * 100, 2)}% of original size"
    )

    return soup


def extract_data(html: str) -> dict:
    g = Goose()
    article = g.extract(raw_html=html)

    logging.info(f"Data extracted from HTML. Title: {article.title}")

    return dict(
        title=article.title,
        content=article.cleaned_text,
    )
