from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from .const import MD_FORMAT, RESULT_FILENAME, RESULT_HTML_FILENAME, RESULT_MD_FILENAME
from .utils import clean_html, extract_data, fetch_html, get_alternate_url


def scrape_article(url: str) -> dict:
    alternate_url = get_alternate_url(url)
    html = fetch_html(alternate_url)
    cleaned_html = clean_html(html)
    data = extract_data(str(cleaned_html))

    return dict(url=url, alternate_url=alternate_url, html=cleaned_html, **data)


def _init_files(version: str, id: str) -> tuple[Path, Path, Path]:
    result_filename = Path(RESULT_FILENAME.format(version=version))
    result_md_filename = Path(RESULT_MD_FILENAME.format(version=version))
    html_filename = Path(RESULT_HTML_FILENAME.format(version=version, url=id))

    result_filename.parent.mkdir(parents=True, exist_ok=True)
    html_filename.parent.mkdir(parents=True, exist_ok=True)

    return result_filename, result_md_filename, html_filename


def process_article(article_url: str) -> dict:
    logging.info(f"Being scraping {article_url}...")

    version = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    id = article_url.replace("/", "_")

    result_filename, result_md_filename, html_filename = _init_files(version, id)

    article_data = scrape_article(article_url)
    article_data["id"] = id

    pd.DataFrame([article_data]).to_csv(
        result_filename,
        mode="a",
        header=not result_filename.exists(),  # only write header on the first iteration
        index=False,
    )

    with open(result_md_filename, "a") as f:
        f.write(MD_FORMAT.format(**article_data))

    with open(html_filename, "w") as f:
        f.write(article_data["html"].prettify())

    logging.info(f"Scraping of {article_url} done.")

    return article_data


def process_articles(article_urls: list[str]) -> list[dict]:
    with ThreadPoolExecutor() as executor:
        return list(
            tqdm(executor.map(process_article, article_urls), total=len(article_urls))
        )
