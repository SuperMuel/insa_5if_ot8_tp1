import numpy as np
import pandas as pd
from tqdm import tqdm

from .metrics_compute import compute_metrics_for_articles
from .parser import arg_parser
from .utils import get_journal_name

args = arg_parser.parse_args()

test_set_df = pd.read_csv(args.test_file).dropna(subset=["url"])
scraped_df = pd.read_csv(args.source_file)

merged_df = pd.merge(scraped_df, test_set_df, on="url", suffixes=("_scraped", "_test"))

missing_test = test_set_df[~test_set_df["url"].isin(merged_df["url"])]

if not missing_test.empty:
    print("Missing test articles:")
    print("\n".join(missing_test["url"].tolist()))

merged_df["title_scraped"] = (
    merged_df["title_scraped"].replace(np.nan, "").replace("\n", " ", regex=True)
)
merged_df["content"] = merged_df["content"].replace("\n", " ", regex=True)
merged_df["title_test"] = (
    merged_df["title_test"].replace("\n", " ", regex=True).tolist()
)
merged_df["all"] = merged_df["all"].replace("\n", " ", regex=True).tolist()

merged_df["journal"] = merged_df["url"].apply(get_journal_name).tolist()

table = []

final_title_scores = []
final_text_scores = []

merged_df["title_similarity"] = pd.NA
merged_df["text_similarity"] = pd.NA

for i, (row_index, row) in tqdm(enumerate(merged_df.iterrows()), total=len(merged_df)):
    title_res = compute_metrics_for_articles(
        "Title", row["title_test"], row["title_scraped"]
    )
    text_res = compute_metrics_for_articles("Content", row["all"], row["content"])

    merged_df.loc[row_index, "title_similarity"] = title_res["avg_similarity"]
    merged_df.loc[row_index, "text_similarity"] = text_res["avg_similarity"]

print(merged_df[["url", "title_similarity", "text_similarity"]])

print(f"Average title: {merged_df["title_similarity"].mean():.2f}")
print(f"Average text: {merged_df['text_similarity'].mean():.2f}")
