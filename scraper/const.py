USER_AGENT = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
HTML_TAG_IGNORE = ["script", "style", "img", "figure"]
HTML_ATTR_IGNORE = ["style"]

MD_FORMAT = (
    "# {title}\n\n[URL]({url}) ([Archive URL]({alternate_url}))\n\n{content}\n\n"
)

RESULT_DIR = "results/{version}"
RESULT_FILENAME = f"{RESULT_DIR}/results.csv"
RESULT_MD_FILENAME = f"{RESULT_DIR}/results.md"
RESULT_HTML_FILENAME = f"{RESULT_DIR}/html/{{url}}.html"
