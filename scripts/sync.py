import json
import os
from urllib.request import urlopen

OUTPUT_FILE = "data/articles.json"

PAGE_SIZE = 150

print("开始同步 Blogger 档案...")


# =========================
# 抓取全部分页
# =========================

feed_articles = []

start_index = 1

while True:

    feed_url = (
        "https://tengkongworld.blogspot.com/"
        f"feeds/posts/default?alt=json"
        f"&max-results={PAGE_SIZE}"
        f"&start-index={start_index}"
    )

    print(f"读取第 {start_index} 篇开始的数据...")

    with urlopen(feed_url) as response:
        data = json.load(response)

    entries = data["feed"].get("entry", [])

    if not entries:
        break

    print(f"本页读取 {len(entries)} 篇")

    for entry in entries:

        article_id = entry["id"]["$t"].split("-")[-1]

        title = entry.get("title", {}).get("$t", "")

        published = entry.get(
            "published", {}
        ).get("$t", "")[:10]

        labels = []

        for category in entry.get("category", []):
            labels.append(
                category.get("term", "")
            )

        content = entry.get(
            "content", {}
        ).get("$t", "")

        feed_articles.append({
            "id": article_id,
            "title": title,
            "published": published,
            "labels": labels,
            "content": content
        })

    start_index += PAGE_SIZE


# =========================
# 读取现有档案
# =========================

existing_articles = []

if os.path.exists(OUTPUT_FILE):

    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            existing_articles = json.load(f)

    except:

        existing_articles = []


# =========================
# 合并
# =========================

articles_by_id = {}

for article in existing_articles:

    articles_by_id[
        article["id"]
    ] = article

for article in feed_articles:

    articles_by_id[
        article["id"]
    ] = article


articles = list(
    articles_by_id.values()
)


# =========================
# 排序
# =========================

articles.sort(
    key=lambda x: x["published"],
    reverse=True
)


# =========================
# 保存
# =========================

os.makedirs(
    "data",
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        articles,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("同步完成")
print("Feed读取数量:", len(feed_articles))
print("档案馆总数量:", len(articles))
print("输出文件:", OUTPUT_FILE)