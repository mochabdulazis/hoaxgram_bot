import feedparser

from rss_sources import RSS_FEEDS

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SIMILARITY_THRESHOLD = 0.15


def get_related_news(query, max_results=4):

    articles = []
    seen_titles = set()

    # =========================
    # Ambil RSS
    # =========================
    for source, url in RSS_FEEDS.items():

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:

                title = entry.title.strip()

                # Remove duplicate
                if title.lower() in seen_titles:
                    continue

                seen_titles.add(title.lower())

                articles.append({
                    "source": source,
                    "title": title,
                    "link": entry.link
                })

        except Exception:
            continue

    # =========================
    # Fallback
    # =========================
    if not articles:
        return []

    # =========================
    # TF-IDF Similarity
    # =========================
    titles = [a["title"] for a in articles]

    documents = [query] + titles

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    ).flatten()

    # =========================
    # Tambahkan score
    # =========================
    for i, score in enumerate(similarity):
        articles[i]["score"] = score

    # =========================
    # Sort similarity
    # =========================
    articles = sorted(
        articles,
        key=lambda x: x["score"],
        reverse=True
    )

    # =========================
    # Threshold filter
    # =========================
    filtered = [
        a for a in articles
        if a["score"] >= SIMILARITY_THRESHOLD
    ]

    return filtered[:max_results]
