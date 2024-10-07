import logging
from pathlib import Path

from rich.logging import RichHandler

from .parser import arg_parser
from .scraper import process_articles

args = arg_parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    handlers=[RichHandler(), logging.FileHandler("scraper.log")],
)

name: str | None = None

if args.urls:
    urls = args.urls
elif args.file:
    name = Path(args.file).stem
    with open(args.file) as f:
        urls = list(filter(lambda u: u, f.readlines()))
else:
    arg_parser.error("Please provide either a list of URLs or a file containing URLs")


process_articles(urls, name=name)
