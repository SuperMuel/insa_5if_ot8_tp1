import logging
import time
from dataclasses import dataclass
from typing import Protocol

import requests
from selenium import webdriver

logger = logging.getLogger(__name__)


class DownloaderError(Exception):
    should_retry: bool

    def __init__(self, *args: object, should_retry: bool = True) -> None:
        super().__init__(*args)
        self.should_retry = should_retry


@dataclass
class DownloadResult:
    url: str
    content: str
    method: str


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
            f"Could not find a snapshot for {url} on the Internet Archive.",
            should_retry=False,
        )

    logger.info(f"Fetching archive with {resource_url}")

    try:
        response = requests.get(resource_url)
    except requests.ConnectionError as e:
        time.sleep(1 ** (retry_n + 1))
        raise DownloaderError(f"Connection error while fetching archive: {e}")

    return DownloadResult(
        url=resource_url,
        content=response.text,
        method="archive",
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

    return DownloadResult(url=url, content=page_source, method="selenium")


def default_downloader(url: str, *, retry_n: int, **kwargs) -> DownloadResult:
    return DownloadResult(
        url=url,
        content=requests.get(url).text,
        method="request",
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

                if not e.should_retry:
                    break

    raise DownloaderError(f"No downloaders could download {url}.")
