import logging

from .parser import arg_parser
from .scraper import process_articles

logging.basicConfig(level=logging.INFO)

args = arg_parser.parse_args()

if args.urls:
    urls = args.urls
elif args.file:
    with open(args.file) as f:
        urls = list(filter(lambda u: u, f.readlines()))
else:
    arg_parser.error("Please provide either a list of URLs or a file containing URLs")


process_articles(urls)
