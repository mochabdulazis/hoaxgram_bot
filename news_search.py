import feedparser
import re

RSS_FEEDS = {
    "CNN Indonesia": "https://www.cnnindonesia.com/rss",
    "Antara": "https://www.antaranews.com/rss/terkini.xml",
    "Tempo": "https://rss.tempo.co",
    "Kumparan": "https://lapi.kumparan.com/v2.0/rss/",
    "Tirto": "https://tirto.id/rss"
}


def extract_keywords(text):

    words = re.findall(r'\w+', text.lower())

    stopwords = {
        "yang", "dan", "di", "ke", "dari",
        "ini", "itu", "ada", "akan"
    }

    keywords = [
        w for w in words
        if len(w) > 3 and w not in stopwords
    ]

    return keywords[:5]


def get_related_news(query, max_results=4):

    keywords = extract_keywords(query)

    results = []
    seen_titles = set()

    for source, url in RSS_FEEDS.items():

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:

                title = entry.title

                if title.lower() in seen_titles:
                    continue

                seen_titles.add(title.lower())

                title_lower = title.lower()

                score = sum(
                    keyword in title_lower
                    for keyword in keywords
                )

                if score > 0:

                    results.append({
                        "source": source,
                        "title": title,
                        "link": entry.link,
                        "score": score
                    })

        except Exception:
            continue

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:max_results]
