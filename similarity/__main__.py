from statistics import mean

import numpy as np
import pandas as pd
from tqdm import tqdm

from .metrics_compute import compute_metrics_for_articles, precision
from .parser import arg_parser
from .utils import get_journal_name, print_similarity_results

args = arg_parser.parse_args()

test_set_df = pd.read_csv(args.test_file)
scraped_df = pd.read_csv(args.source_file)

merged_df = scraped_df.merge(test_set_df, on=["url"], suffixes=("_scraped", "_test"))

all_titles = (
    merged_df["title_scraped"].replace(np.nan, "").replace("\n", " ", regex=True)
)
all_texts = merged_df["content"].replace("\n", " ", regex=True)

journals = merged_df["url"].apply(get_journal_name).tolist()

titles = merged_df["title_test"].replace("\n", " ", regex=True).tolist()
contents = merged_df["all"].replace("\n", " ", regex=True).tolist()

table = []
final_title_scores = []
final_text_scores = []

for i in tqdm(range(len(merged_df))):
    journal = journals[i]
    title = titles[i]
    content = contents[i]

    final_title_scores.append(
        compute_metrics_for_articles(
            table, i + 1, journal, "Title", title, all_titles[i]
        )
    )
    final_text_scores.append(
        compute_metrics_for_articles(
            table, i + 1, journal, "Content", content, all_texts[i]
        )
    )

print(f"Average CSS over all titles: {mean(final_title_scores):.{precision}f}")
print(f"Average CSS over all texts: {mean(final_text_scores):.{precision}f}\n")

print_similarity_results(table)
