import logging
from typing import Callable

import requests
from waybackpy import WaybackMachineCDXServerAPI
from waybackpy.exceptions import NoCDXRecordFound

from .const import USER_AGENT

logger = logging.getLogger(__name__)


class DownloaderError(Exception):
    pass


Downloader = Callable[[str], tuple[str, str]]

INTERNET_ARCHIVE_URL = "http://archive.org/wayback/available?url={url}"


def wayback_machine_cdx_downloader(
    url: str, *, user_agent: str = USER_AGENT, **kwargs
) -> tuple[str, str]:
    try:
        cdx_api = WaybackMachineCDXServerAPI(url=url, user_agent=user_agent, **kwargs)
        alternate_url = cdx_api.newest().archive_url

        logger.info(f"Alternate URL for {url} is {alternate_url}")

        return alternate_url, requests.get(url).text
    except NoCDXRecordFound:
        raise DownloaderError(
            f"No alternate URL found for {url} using Wayback Machine CDX API."
        )


def internet_archive_wayback_downloader(
    url: str, *, retries: int = 3
) -> tuple[str, str]:
    availability_url = INTERNET_ARCHIVE_URL.format(url=url)

    response = None

    for _ in range(retries):
        try:
            response = requests.get(availability_url)
            break
        except requests.RequestException as e:
            logger.warning(f"Error fetching {availability_url}: {e}. Retrying...")
            continue

    if not response:
        raise DownloaderError(f"Could not fetch {availability_url}.")

    response_json = response.json()

    try:
        resource_url = response_json["archived_snapshots"]["closest"]["url"]
    except KeyError:
        raise DownloaderError(
            f"Could not find a snapshot for {url} on the Internet Archive."
        )

    return resource_url, requests.get(resource_url).text


def default_downloader(url: str) -> tuple[str, str]:
    return url, requests.get(url).text


DOWNLOADERS: list[Downloader] = [
    internet_archive_wayback_downloader,
    default_downloader,
]


def download_resource(
    url: str, *, downloaders: list[Downloader] = DOWNLOADERS
) -> tuple[str, str]:
    for downloader in downloaders:
        try:
            return downloader(url)
        except DownloaderError as e:
            logger.warning(e)

    raise DownloaderError(f"No downloaders could download {url}.")
