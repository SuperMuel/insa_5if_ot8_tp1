from functools import cache
from bs4 import BeautifulSoup
import requests
from waybackpy import WaybackMachineCDXServerAPI
from waybackpy.exceptions import NoCDXRecordFound
import logging
from goose3 import Goose

from .const import HTML_ATTR_IGNORE, HTML_TAG_IGNORE, USER_AGENT


@cache
def get_alternate_url(url: str, *, user_agent: str = USER_AGENT, **kwargs) -> str:
    try:
        cdx_api = WaybackMachineCDXServerAPI(url=url, user_agent=user_agent, **kwargs)
        alternate_url = cdx_api.newest().archive_url

        logging.info(f"Alternate URL for {url} is {alternate_url}")

        return alternate_url
    except NoCDXRecordFound:
        logging.info(f"No alternate URL found for {url}. Using original URL.")
        return url


@cache
def fetch_html(url: str) -> str:
    return requests.get(url).text


@cache
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


@cache
def extract_data(html: str) -> dict:
    g = Goose()
    article = g.extract(raw_html=html)

    logging.info(f"Data extracted from HTML. Title: {article.title}")

    return dict(
        title=article.title,
        content=article.cleaned_text,
    )
