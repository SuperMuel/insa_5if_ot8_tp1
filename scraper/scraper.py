import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from .const import MD_FORMAT, RESULT_FILENAME, RESULT_HTML_FILENAME, RESULT_MD_FILENAME
from .downloader import download_resource
from .utils import clean_html, extract_data

logger = logging.getLogger(__name__)


def scrape_article(url: str) -> dict:
    resource = download_resource(url)
    cleaned_html = clean_html(resource.content)
    data = extract_data(str(cleaned_html))

    return dict(url=url, used_url=resource.url, html=cleaned_html, **data)


def _init_files(version: str, id: str) -> tuple[Path, Path, Path]:
    result_filename = Path(RESULT_FILENAME.format(version=version))
    result_md_filename = Path(RESULT_MD_FILENAME.format(version=version, url=id))
    html_filename = Path(RESULT_HTML_FILENAME.format(version=version, url=id))

    result_filename.parent.mkdir(parents=True, exist_ok=True)
    result_md_filename.parent.mkdir(parents=True, exist_ok=True)
    html_filename.parent.mkdir(parents=True, exist_ok=True)

    return result_filename, result_md_filename, html_filename


def process_article(
    article_url: str, version: str | None = None, *, dry_run: bool = False
) -> dict:
    logger.info(f"Being scraping {article_url}...")

    version = version if version else datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    id = article_url.replace("/", "_")

    result_filename, result_md_filename, html_filename = _init_files(version, id)

    article_data = scrape_article(article_url)
    article_data["id"] = id

    if not dry_run:
        pd.DataFrame([article_data]).fillna("").to_csv(
            result_filename,
            mode="a",
            header=not result_filename.exists(),  # only write header on the first iteration
            index=False,
        )

        with open(result_md_filename, "w") as f:
            f.write(MD_FORMAT.format(**article_data))

        with open(html_filename, "w") as f:
            f.write(article_data["html"].prettify())

        logger.info(
            f"Saved data to \n\tCSV: '{result_filename}'\n\tMD: '{result_md_filename}'\n\tHTML: '{html_filename}'."
        )
    logger.info(f"Scraping of {article_url} done.")

    return article_data


def process_articles(
    article_urls: list[str],
    *,
    name: str | None = None,
    version: str | None = None,
    dry_run: bool = False,
) -> list[dict]:
    version = (
        version
        if version is not None
        else datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + (f"_{name}" if name else "")
    )

    result_filename = Path(RESULT_FILENAME.format(version=version))

    if result_filename.exists():
        loaded_data = pd.read_csv(result_filename)

        articles_urls_series = pd.Series(article_urls)
        article_urls = articles_urls_series[
            ~articles_urls_series.isin(loaded_data["url"])
        ].tolist()

        logger.info(f"Ignoring {len(loaded_data)} already scraped articles.")

    logger.info(f"Starting scraping of {len(article_urls)} articles for {version}...")

    res = list(
        process_article(article_url, version, dry_run=dry_run)
        for article_url in tqdm(article_urls)
    )

    logger.info(f"Scraping of {len(article_urls)} articles done.")

    return res

    # with ThreadPoolExecutor() as executor:
    #     return list(
    #         tqdm(
    #             executor.map(
    #                 process_article, article_urls, [version] * len(article_urls)
    #             ),
    #             total=len(article_urls),
    #         )
    #     )
