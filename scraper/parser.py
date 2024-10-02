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
