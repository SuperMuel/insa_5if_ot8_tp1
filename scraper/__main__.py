from .scraper import process_articles
from .parser import arg_parser

args = arg_parser.parse_args()

if args.urls:
    urls = args.urls
elif args.file:
    with open(args.file) as f:
        urls = f.readlines()
else:
    arg_parser.error("Please provide either a list of URLs or a file containing URLs")


process_articles(urls)
