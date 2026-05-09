import feedparser
from rss_sources import RSS_FEEDS

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_related_news(query, max_results=4):
    articles = []

    # Ambil semua berita dari RSS
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries:
            title = entry.title

            articles.append({
                "source": source,
                "title": title,
                "link": entry.link
            })

    # Kalau tidak ada artikel
    if not articles:
        return []

    # TF-IDF
    titles = [article["title"] for article in articles]

    documents = [query] + titles

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Query vs semua judul
    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    ).flatten()

    # Tambahkan similarity score
    for i, score in enumerate(similarity):
        articles[i]["score"] = score

    # Urutkan
    articles = sorted(
        articles,
        key=lambda x: x["score"],
        reverse=True
    )

    # Filter score kecil
    filtered = [a for a in articles if a["score"] > 0.1]

    return filtered[:max_results]
