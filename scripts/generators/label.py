import os


def generate_label_pages(
    articles,
    gallery_labels,
    get_collection_default_view,
    get_collection_default_sort,
    make_slug,
    get_article_image_path,
    build_article_filename,
):
    os.makedirs("labels", exist_ok=True)
    label_articles = {}
    for article in articles:
        for label in article["labels"]:
            if label not in label_articles:
                label_articles[label] = []
            label_articles[label].append(article)
    for label, articles_list in label_articles.items():
        has_gallery = label in gallery_labels
        default_view = get_collection_default_view(label)
        default_sort = get_collection_default_sort(label)

        filepath = f"labels/{make_slug(label)}.html"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1">
    <title>{label}</title>

    <style>

    #gallery-view {{

        display: grid;

        grid-template-columns:

            repeat(

                auto-fill,

                minmax(

                    220px,

                    1fr

                )

            );

        gap: 16px;

    }}

    .gallery-card {{

        border: 1px solid #ddd;

        border-radius: 8px;

        overflow: hidden;

    }}

    .gallery-card img {{

        width: 100%;

        display: block;

    }}

    .gallery-card p {{

        padding: 10px;

        font-weight: bold;

    }}

    </style>
</head>
<body
    data-default-view="{default_view}"
    data-default-sort="{default_sort}"
>
""")

            parent_label = ""

            for article in articles_list:
                if article["labels"] and article["labels"][0] != label:
                    parent_label = article["labels"][0]

                    break

            if parent_label:
                f.write(
                    f"<p>"
                    f'<a href="../index.html">'
                    f"首页"
                    f"</a> / "
                    f'<a href="{make_slug(parent_label)}.html">'
                    f"{parent_label}"
                    f"</a> / "
                    f"{label}"
                    f"</p>"
                )

            else:
                f.write(f'<p><a href="../index.html">首页</a> / {label}</p>')

            f.write(f"<h1>{label}</h1>")

            f.write("""
<div id="reading-progress">
</div>

<div id="next-reading">
</div>
""")
            if has_gallery:
                f.write("""
<p>
<button onclick="sortAsc()">正序</button>
<button onclick="sortDesc()">倒序</button>
</p>

<p>
<button onclick="showListMode()">📄 列表模式</button>
<button onclick="showGalleryMode()">🖼 图鉴模式</button>
</p>
""")

            else:
                f.write("""
<p>
<button onclick="sortAsc()">正序</button>
<button onclick="sortDesc()">倒序</button>
</p>
""")

            f.write("""
<ul id="article-list">
""")

            for index, article in enumerate(articles_list):
                f.write(
                    f'''
        <li
            data-index="{index}"
            data-title="{article["title"]}"
            data-image="{get_article_image_path(article, 1)}"
        >
            <span class="read-mark">○</span>

            <a href="../articles/{build_article_filename(article)}">
                {article["title"]}
            </a>

        </li>
        '''
                )
            f.write("""
    </ul>

""")

            if has_gallery:
                f.write("""

<div
    id="gallery-view"
    style="display:none;"
>
</div>

""")

            f.write("""

<script>                                       

function showListMode() {

    document.getElementById(
        "article-list"
    ).style.display = "block";

    document.getElementById(
        "gallery-view"
    ).style.display = "none";

    localStorage.setItem(
        "viewMode",
        "list"
    );

}

function rebuildGallery() {

    const gallery =
        document.getElementById(
            "gallery-view"
        );

    gallery.innerHTML = "";

    const galleryItems =
        document.querySelectorAll(
            "#article-list li"
        );

    galleryItems.forEach(item => {

        const image =
            item.dataset.image;

        const title =
            item.dataset.title;

        const link =
            item.querySelector(
                "a"
            ).href;

        gallery.innerHTML += `

<div class="gallery-card">

    <a href="${link}">

        <img
            src="${image}"
            alt="${title}"
        >

        <p>
            ${title}
        </p>

    </a>

</div>

`;

    });

}
                                        
function showGalleryMode() {

    document.getElementById(
        "article-list"
    ).style.display = "none";

    const gallery =
        document.getElementById(
            "gallery-view"
        );

    gallery.style.display =
        "grid";

    rebuildGallery();

    localStorage.setItem(
        "viewMode",
        "gallery"
    );

}
                    
function sortAsc() {

    const list =
        document.getElementById(
            "article-list"
        );

    const items =
        Array.from(
            list.children
        );

    items.sort(
        (a, b) =>
        Number(b.dataset.index)
        -
        Number(a.dataset.index)
    );

    list.innerHTML = "";

    items.forEach(item => {

        list.appendChild(item);

    });

    localStorage.setItem(
        "sortOrder",
        "asc"
    );

    if (
        document.getElementById(
            "gallery-view"
        ).style.display !== "none"
    ) {

        rebuildGallery();

    }

}                    

function sortDesc() {

    const list =
        document.getElementById(
            "article-list"
        );

    const items =
        Array.from(
            list.children
        );

    items.sort(
        (a, b) =>
        Number(a.dataset.index)
        -
        Number(b.dataset.index)
    );

    list.innerHTML = "";

    items.forEach(item => {

        list.appendChild(item);

    });

    localStorage.setItem(
        "sortOrder",
        "desc"
    );
    if (
    document.getElementById(
        "gallery-view"
    ).style.display !== "none"
    ) {

    rebuildGallery();

    }                

}

function initializeReadingHistory() {

    const history = JSON.parse(

        localStorage.getItem(

            "readingHistory"

        ) || "[]"

    );

    const readTitles = history.map(

        item => item.title

    );

    document

        .querySelectorAll(

            "li[data-title]"

        )

        .forEach(li => {

            const title =

                li.dataset.title;

            if (

                readTitles.includes(title)

            ) {

                li.querySelector(

                    ".read-mark"

                ).textContent = "✓";

            }

        });

    const totalArticles = document

        .querySelectorAll(

            "li[data-title]"

        ).length;

    const readCount = document

        .querySelectorAll(

            ".read-mark"

        );

    let finished = 0;

    readCount.forEach(mark => {

        if (

            mark.textContent === "✓"

        ) {

            finished++;

        }

    });

    const percent = Math.round(

        finished * 100 / totalArticles

    );

    document.getElementById(

        "reading-progress"

    ).innerHTML = `

        <p>

            已阅读：

            ${finished}

            /

            ${totalArticles}

            (${percent}%)

        </p>

    `;

}

function initializeSort() {

    const savedOrder =

        localStorage.getItem(
            "sortOrder"
        );

    if (
        savedOrder === "asc"
    ) {

        sortAsc();

        return;

    }

    if (
        savedOrder === "desc"
    ) {

        sortDesc();

        return;

    }

    const defaultSort =

        document.body.dataset.defaultSort;

    if (
        defaultSort === "desc"
    ) {

        sortDesc();

    } else {

        sortAsc();

    }

}
                    
                    function initializeView() {

    const savedView =

        localStorage.getItem(
            "viewMode"
        );

    if (
        savedView === "gallery"
    ) {

        showGalleryMode();

        return;

    }

    if (
        savedView === "list"
    ) {

        showListMode();

        return;

    }

    const defaultView =

        document.body.dataset.defaultView;

    if (
        defaultView === "gallery"
    ) {

        showGalleryMode();

    } else {

        showListMode();

    }

}

function initializePage() {

    initializeReadingHistory();

    initializeSort();

    initializeView();

}

initializePage();
                                                                                                  
</script>

</body>
</html>
""")
