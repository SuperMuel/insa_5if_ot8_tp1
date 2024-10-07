from argparse import ArgumentParser

arg_parser = ArgumentParser()

arg_parser.add_argument(
    "--url",
    "-u",
    type=str,
    dest="urls",
    nargs="+",
    help="URLs of articles to scrape",
)

arg_parser.add_argument(
    "--file",
    "-f",
    type=str,
    dest="file",
    help="File containing URLs of articles to scrape",
)

arg_parser.add_argument(
    "--version",
    type=str,
    help="Version of the scraping result (used to continue a previous scraping)",
)

arg_parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Do not save any data",
)

arg_parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Print debug messages",
)
