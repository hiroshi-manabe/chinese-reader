#!/usr/bin/env python3
import pathlib
import re

# Directory where this script and the .txt files live
BASE_DIR = pathlib.Path(__file__).parent

SITE_TITLE = "Chinese Reading"
CSS_FILE = "style.css"
INDEX_FILE = "index.html"

# Pattern: 小(xiǎo) 红(hóng) 帽(mào) ...
RUBY_RE = re.compile(r'([\u4e00-\u9fff]+)\(([^)]+)\)')


def extract_title(text: str, fallback: str) -> str:
    """
    Use the first non-empty line to make a title.
    Example: 小(xiǎo) 红(hóng) 帽(mào) -> 小红帽
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return fallback

    first = lines[0]
    # Remove (pinyin)
    no_pinyin = RUBY_RE.sub(r'\1', first)
    # Remove spaces: "小 红 帽" -> "小红帽"
    title = "".join(no_pinyin.split())
    return title or fallback


def to_ruby_html(text: str) -> str:
    """
    Convert 小(xiǎo) 红(hóng) 帽(mào) style text into ruby HTML.
    Blank lines in the .txt become paragraph breaks (<p>).
    """

    def repl(match: re.Match) -> str:
        han = match.group(1)
        py = match.group(2)
        return f"<ruby>{han}<rt>{py}</rt></ruby>"

    paragraphs = []
    for block in text.strip().split("\n\n"):
        block = block.strip()
        if not block:
            continue
        html_block = RUBY_RE.sub(repl, block)
        paragraphs.append(f"<p>{html_block}</p>")
    return "\n\n".join(paragraphs)


def write_story_html(txt_path: pathlib.Path):
    """
    Read one .txt file, write a same-name .html file, and
    return (html_filename, display_title).
    """
    html_path = txt_path.with_suffix(".html")
    text = txt_path.read_text(encoding="utf-8")

    title = extract_title(text, txt_path.stem)
    body_html = to_ruby_html(text)

    html = f"""<!doctype html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="{CSS_FILE}">
</head>
<body>
  <a href="{INDEX_FILE}" class="back">← Back to list</a>
  <h1>{title}</h1>

{body_html}

</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")
    return html_path.name, title


def write_index(pages):
    """
    pages: list of (html_filename, title)
    """
    items = "\n".join(
        f'    <li><a href="{fname}">{title}</a></li>'
        for fname, title in pages
    )

    index_html = f"""<!doctype html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <title>{SITE_TITLE}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="{CSS_FILE}">
</head>
<body>
  <h1>{SITE_TITLE}</h1>

  <ul class="story-list">
{items}
  </ul>
</body>
</html>
"""
    (BASE_DIR / INDEX_FILE).write_text(index_html, encoding="utf-8")


def ensure_css():
    """
    Create a default style.css if it doesn't exist.
    (If you later edit style.css by hand, this script will not overwrite it.)
    """
    css_path = BASE_DIR / CSS_FILE
    if css_path.exists():
        return

    css = """body {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 1.4rem;
  line-height: 1.8;
}

a {
  color: inherit;
}

a.back {
  display: inline-block;
  margin-bottom: 1rem;
  text-decoration: none;
}

ul.story-list {
  padding-left: 1.2rem;
}

ul.story-list li {
  margin: 0.4rem 0;
}

ruby {
  ruby-position: over;
}

rt {
  font-size: 0.6em;
  color: #555;
}
"""
    css_path.write_text(css, encoding="utf-8")


def main():
    ensure_css()

    txt_files = sorted(BASE_DIR.glob("*.txt"))
    pages = []

    for txt_path in txt_files:
        html_name, title = write_story_html(txt_path)
        pages.append((html_name, title))

    write_index(pages)


if __name__ == "__main__":
    main()
