import re

from urllib.parse import quote

from pypinyin import lazy_pinyin

import json
import os
from urllib.request import (
    urlopen,
    urlretrieve
)

OUTPUT_FILE = "data/articles.json"

PAGE_SIZE = 150

print("开始同步 Blogger 档案...")

def make_slug(text):

    text = re.sub(
        r"[《》【】（）()：:、，。！？\s\-]",
        "",
        text
    )

    return "".join(
        lazy_pinyin(text)
    )


def build_article_filename(article):

    if article["labels"]:

        label = article["labels"][-1]

    else:

        label = "archive"

    slug = make_slug(label)

    return (
        f"{article['published']}"
        f"-{slug}"
        f"-{article['id']}.html"
    )

def generate_html_files(articles):

    os.makedirs(
        "articles",
        exist_ok=True
    )

    for article in articles:

        current_label = ""

        if article["labels"]:
            current_label = article["labels"][-1]

        same_label_articles = []

        for a in articles:

            if current_label in a["labels"]:
                same_label_articles.append(a)

        same_label_articles.sort(
            key=lambda x: x["published"]
        )        

        current_index = same_label_articles.index(
            article
        )

        previous_article = None
        next_article = None

        if current_index > 0:

            previous_article = (
                same_label_articles[
                    current_index - 1
                ]
            )

        if current_index < (
            len(same_label_articles) - 1
        ):

            next_article = (
                same_label_articles[
                    current_index + 1
                ]
            )

        filename = build_article_filename(
            article
        )

        filepath = os.path.join(
            "articles",
            filename
        )

        label_links = []

        for label in article["labels"]:

            label_slug = make_slug(label)

            label_links.append(
                f'<a href="../labels/{label_slug}.html">{label}</a>'
            )

        labels_html = " / ".join(
            label_links
        )

        content = article["content"]

        imgs = re.findall(
            r'<img[^>]+src="([^"]+)"',
            content
        )

        for index, img_url in enumerate(
            imgs,
            start=1
        ):

            local_image = (
                f"../assets/images/"
                f"{article['id']}-{index}.jpg"
            )

            content = content.replace(
                img_url,
                local_image
            )

        navigation_html = ""

        if previous_article:

            navigation_html += (
                f'<p>← '
                f'<a href="{build_article_filename(previous_article)}">'
                f'{previous_article["title"]}'
                f'</a></p>'
            )

        if next_article:

            navigation_html += (
                f'<p>'
                f'<a href="{build_article_filename(next_article)}">'
                f'{next_article["title"]}'
                f'</a> →</p>'
            )

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">

<head>

<meta charset="utf-8">

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>{article['title']}</title>

<style>

body{{
    max-width:900px;
    margin:auto;
    padding:20px;
    font-family:Arial, Helvetica, sans-serif;
    line-height:1.8;
}}

img{{
    max-width:100%;
    height:auto;
}}

</style>

</head>

<body>

<p>
<a href="../index.html">
← 返回首页
</a>
</p>

<h1>
{article['title']}
</h1>

<p>
发布日期：
{article['published']}
</p>

<p>
标签：
{labels_html}
</p>

<hr>

{content}

<hr>

<h3>上一篇 / 下一篇</h3>

{navigation_html}

<hr>

<p>
档案编号：
{article['id']}
</p>

<p>
来源：
腾空世界观档案馆
</p>

</body>

</html>
"""

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)

def generate_label_pages(articles):
    os.makedirs("labels", exist_ok=True)
    label_articles = {}
    for article in articles:
        for label in article["labels"]:
            if label not in label_articles:
                label_articles[label] = []
            label_articles[label].append(article)
    for label, articles_list in label_articles.items():
        filename = f"labels/{make_slug(label)}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{label}</title>
</head>
<body>
    <h1>{label}</h1>
    <ul>
""")
            for article in articles_list:
                f.write(f'        <li><a href="../articles/{build_article_filename(article)}">{article["title"]}</a></li>\n')
            f.write("""    </ul>
</body>
</html>
""")

def download_images(articles):

    os.makedirs(
        "assets/images",
        exist_ok=True
    )

    total = 0

    for article in articles:

        imgs = re.findall(
            r'<img[^>]+src="([^"]+)"',
            article["content"]
        )

        for index, img_url in enumerate(
            imgs,
            start=1
        ):

            original_url = img_url

            img_url = re.sub(
                r"/s\d+/",
                "/s0/",
                img_url
            )

            img_url = re.sub(
                r"/w\d+-h\d+/",
                "/s0/",
                img_url
            )

            img_url = re.sub(
                r"=w\d+-h\d+$",
                "=s0",
                img_url
            )

            if (
                original_url == img_url
                and "/s0/" not in img_url
                and "=s0" not in img_url
                and "/img/a/" not in img_url
            ):

                print(
                    "未处理图片格式:",
                    img_url
                )

            filename = (
                f"{article['id']}"
                f"-{index}.jpg"
            )

            filepath = os.path.join(
                "assets/images",
                filename
            )

            if os.path.exists(
                filepath
            ):

                continue

            try:

                if "307230326693859030" in filename:

                    print()
                    print("===== 实际下载URL =====")
                    print(img_url)
                    print()

                urlretrieve(
                    img_url,
                    filepath
                )

                total += 1

                if "25-1.jpg" in img_url:
                    print()
                    print("===== 外星人图片 =====")
                    print(img_url)
                    print()

                print(
                    "下载:",
                    filename
                )

            except Exception as e:

                print(
                    "失败:",
                    img_url
                )

                print(

                    e

                 )

    print()
    print(
        "新增图片:",
        total
    )
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

for article in articles:

    article["filename"] = (
        build_article_filename(article)
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
print()

print(
    build_article_filename(
        articles[0]
    )
)
print()
print(
    make_slug("《心经》佛界之解1")
)

print(
    make_slug("难经心神难篇")
)
print()
print("===== 难经人间难篇排序 =====")

test_articles = []

for a in articles:

    if "难经人间难篇" in a["labels"]:
        test_articles.append(a)

test_articles.sort(
    key=lambda x: x["published"]
)

for a in test_articles:

    print(
        a["published"],
        a["title"]
    )

generate_html_files(
    articles
)
generate_label_pages(
    articles
)
download_images(
    articles
)
print()
print(
    "静态HTML数量:",
    len(articles)
)
