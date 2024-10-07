import logging
import time
from dataclasses import dataclass
from typing import Protocol

import requests
from selenium import webdriver

logger = logging.getLogger(__name__)


class DownloaderError(Exception):
    pass


@dataclass
class DownloadResult:
    url: str
    content: str


class Downloader(Protocol):
    def __call__(self, url: str, *, retry_n: int, **kwargs) -> DownloadResult: ...


INTERNET_ARCHIVE_URL = "http://archive.org/wayback/available?url={url}"


def internet_archive_wayback_downloader(
    url: str, *, retry_n: int, **kwargs
) -> DownloadResult:
    availability_url = INTERNET_ARCHIVE_URL.format(url=url)
    logger.info(f"Checking availability with {availability_url}")

    try:
        response = requests.get(availability_url)
    except requests.RequestException as e:
        raise DownloaderError(f"Error checking availability: {e}")

    response_json = response.json()
    logger.debug(f"Internet Archive response for {url}: {response_json}")

    try:
        resource_url = response_json["archived_snapshots"]["closest"]["url"]
    except KeyError:
        raise DownloaderError(
            f"Could not find a snapshot for {url} on the Internet Archive."
        )

    logger.info(f"Fetching archive with {resource_url}")

    return DownloadResult(
        url=resource_url,
        content=requests.get(resource_url).text,
    )


def selenium_downloader(url: str, *, retry_n: int, **kwargs) -> DownloadResult:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(1 ** (retry_n + 1))

        page_source = driver.page_source
    except Exception as e:
        raise DownloaderError(f"Error downloading {url} with Selenium: {e}")
    finally:
        driver.quit()

    return DownloadResult(url=url, content=page_source)


def default_downloader(url: str, *, retry_n: int, **kwargs) -> DownloadResult:
    return DownloadResult(
        url=url,
        content=requests.get(url).text,
    )


DOWNLOADERS: list[Downloader] = [
    internet_archive_wayback_downloader,
    selenium_downloader,
    default_downloader,
]


def download_resource(
    url: str,
    *,
    downloaders: list[Downloader] = DOWNLOADERS,
    retries: int = 3,
) -> DownloadResult:
    for downloader in downloaders:
        for i in range(retries):
            logger.info(
                f"Downloading using '{downloader.__name__}' (attempt {i + 1})"  # type: ignore
            )

            try:
                return downloader(url, retry_n=i)
            except DownloaderError as e:
                logger.warning(f"Error downloading with '{downloader.__name__}': {e}")  # type: ignore

    raise DownloaderError(f"No downloaders could download {url}.")
