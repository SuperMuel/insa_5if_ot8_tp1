import editdistance
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def jaccard_similarity(text1, text2):
    set1 = set(text1.split())
    set2 = set(text2.split())

    return len(set1.intersection(set2)) / len(set1.union(set2))


def cosine_sim(text1, text2):
    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()

    cos_sim = cosine_similarity(vectors)

    return cos_sim[0][1]


def edit_score(text1, text2):
    return 1 - (editdistance.eval(text1, text2) / max(len(text1), len(text2)))
