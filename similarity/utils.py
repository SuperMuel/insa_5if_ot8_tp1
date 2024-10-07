from urllib.parse import urlparse

from tabulate import tabulate

from .metrics_compute import precision, threshold


def get_journal_name(url):
    second_level_domains = ["com.cn", "co.uk", "org.cn", "net.cn", "fr", "de", "es"]

    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split(".")

    if len(domain_parts) > 2 and ".".join(domain_parts[-2:]) in second_level_domains:
        return domain_parts[-3]

    elif len(domain_parts) > 2:
        return domain_parts[-2]

    else:
        return domain_parts[0]


def print_similarity_results(table):
    headers = [
        "Article #",
        "Journal Name",
        "Type",
        "N-gram Similarity",
        "Edit Distance (Score)",
        #'Cosine Similarity',
        "Combined Syntaxic Similarity (CSS)",
        f"CSS > {threshold}",
    ]

    print(
        tabulate(
            table,
            headers=headers,
            tablefmt="grid",
            floatfmt=f".{precision}f",
            colalign=(
                "center",
                "center",
                "center",
                "center",
                "center",
                "center",
                "center",
            ),
        )
    )
