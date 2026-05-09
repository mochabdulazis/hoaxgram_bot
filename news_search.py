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

    text = text.lower()

    stopwords = {
        "yang", "dan", "di", "ke", "dari",
        "ini", "itu", "ada", "akan",
        "dengan", "karena", "setelah",
        "terkait", "dalam", "untuk",
        "para", "sebuah", "oleh"
    }

    words = re.findall(r'\w+', text)

    keywords = []

    for word in words:

        if (
            len(word) > 4 and
            word not in stopwords
        ):
            keywords.append(word)

    # Remove duplicate
    keywords = list(dict.fromkeys(keywords))

    return keywords[:10]


def get_related_news(query, max_results=4):
    keywords = extract_keywords(query)
    print("KEYWORDS:", keywords)
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

                matched_keywords = [
                    keyword
                    for keyword in keywords
                    if keyword in title_lower
                ]

                score = len(matched_keywords)

                print(title, matched_keywords, score)

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
