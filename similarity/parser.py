from argparse import ArgumentParser

arg_parser = ArgumentParser()

arg_parser.add_argument(
    "--test-file",
    "-tf",
    type=str,
    dest="test_file",
    help="File containing tested sources",
)

arg_parser.add_argument(
    "--scrape-file",
    "-sf",
    type=str,
    dest="source_file",
    help="File containing scraped sources",
)
