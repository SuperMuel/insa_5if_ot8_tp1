import editdistance
from ngram import NGram

from .metrics import cosine_sim, edit_score

precision = 2
threshold = 0.95


def compute_metrics_for_articles(
    table, article_number, journal, article_type, manual, scraped, n_title=1, n_text=1
):
    ngram_similarity = (
        NGram.compare(manual, scraped, N=n_title)
        if article_type == "Title"
        else NGram.compare(manual, scraped, N=n_text)
    )

    edit_dist = editdistance.eval(manual, scraped)
    edit_sim = edit_score(manual, scraped)

    cos_sim = cosine_sim(manual, scraped)

    avg_similarity = (ngram_similarity + edit_sim) / 2
    # avg_similarity = (ngram_similarity + edit_sim + cos_sim) / 3

    mark = "X" if avg_similarity >= threshold else "-"

    table.append(
        [
            article_number,
            journal,
            article_type,
            ngram_similarity,
            f"{edit_dist} ({edit_sim:.{precision}f})",
            # cos_sim,
            avg_similarity,
            mark,
        ]
    )

    return avg_similarity
