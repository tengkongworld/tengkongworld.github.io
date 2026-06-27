import os
import re


def generate_html_files(
    articles,
    make_slug,
    build_article_filename,
    get_article_image_path,
):

    os.makedirs("articles", exist_ok=True)

    for article in articles:
        current_label = ""

        if article["labels"]:
            current_label = article["labels"][-1]

        same_label_articles = []

        for a in articles:
            if current_label in a["labels"]:
                same_label_articles.append(a)

        same_label_articles.sort(key=lambda x: x["published"])

        current_index = same_label_articles.index(article)

        previous_article = None
        next_article = None

        if current_index > 0:
            previous_article = same_label_articles[current_index - 1]

        if current_index < (len(same_label_articles) - 1):
            next_article = same_label_articles[current_index + 1]

        filename = build_article_filename(article)

        filepath = os.path.join("articles", filename)

        label_links = []

        for label in article["labels"]:
            label_slug = make_slug(label)

            label_links.append(f'<a href="../labels/{label_slug}.html">{label}</a>')

        labels_html = " / ".join(label_links)

        breadcrumb_links = ['<a href="../index.html">首页</a>']

        for label in article["labels"]:
            label_slug = make_slug(label)

            breadcrumb_links.append(
                f'<a href="../labels/{label_slug}.html">{label}</a>'
            )

        back_to_label = f"""
<p>
{" / ".join(breadcrumb_links)}
</p>
"""

        content = article["content"]

        imgs = re.findall(r'<img[^>]+src="([^"]+)"', content)

        local_images = {}

        for index, img_url in enumerate(imgs, start=1):
            local_image = get_article_image_path(article, index)

            local_images[img_url] = local_image

            content = content.replace(img_url, local_image)

        blogger_image_links = re.findall(
            r'<a\b[^>]*href="(https://blogger\.googleusercontent\.com/[^"]+)"',
            content,
        )

        for index, href in enumerate(blogger_image_links, start=1):
            local_image = local_images.get(href)

            if local_image is None and index <= len(imgs):
                local_image = get_article_image_path(article, index)

            if local_image:
                content = content.replace(f'href="{href}"', f'href="{local_image}"')

        navigation_html = ""

        if previous_article:
            navigation_html += (
                f"<p>← "
                f'<a href="{build_article_filename(previous_article)}">'
                f"{previous_article['title']}"
                f"</a></p>"
            )

        if next_article:
            navigation_html += (
                f"<p>"
                f'<a href="{build_article_filename(next_article)}">'
                f"{next_article['title']}"
                f"</a> →</p>"
            )

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">

<head>

<meta charset="utf-8">

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>{article["title"]}</title>

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

<body>

{back_to_label}

<h1>
{article["title"]}
</h1>

<p>
发布日期：
{article["published"]}
</p>

<hr>

{content}

<hr>

<h3>上一篇 / 下一篇</h3>

{navigation_html}

<hr>

<p>
档案编号：
{article["id"]}
</p>

<p>
来源：
腾空世界观档案馆
</p>

<script>

const currentArticle = {{

    title: "{article["title"]}",

    url: window.location.pathname,

    time: Date.now()

}};



/* 最近阅读 */

let history = JSON.parse(

    localStorage.getItem(
        "readingHistory"
    ) || "[]"

);

history = history.filter(

    item => item.url !== currentArticle.url

);

history.unshift(
    currentArticle
);

history = history.slice(
    0,
    10
);

localStorage.setItem(

    "readingHistory",

    JSON.stringify(history)

);



/* 累计阅读 */

let archive = JSON.parse(

    localStorage.getItem(
        "readingArchive"
    ) || "[]"

);

if (

    !archive.includes(
        currentArticle.url
    )

) {{

    archive.push(
        currentArticle.url
    );

    localStorage.setItem(

        "readingArchive",

        JSON.stringify(
            archive
        )

    );

}}

</script>

</body>

</html>
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
