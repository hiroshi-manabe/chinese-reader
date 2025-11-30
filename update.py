#!/usr/bin/env python3
import pathlib
import re

BASE_DIR = pathlib.Path(__file__).parent

SITE_TITLE = "Chinese Reading"
CSS_FILE = "style.css"
INDEX_FILE = "index.html"

# Pattern: 小(xiǎo) 红(hóng) 帽(mào)
RUBY_RE = re.compile(r'([\u4e00-\u9fff]+)\(([^)]+)\)')


def split_title_and_body(text: str):
    """
    Take the first non-empty line as title line (for generating the title),
    and return (title_line, body_text).
    The title line is NOT included in the body.
    """
    lines = text.splitlines()
    title_line = None
    body_start_idx = 0

    for idx, raw in enumerate(lines):
        if raw.strip():
            title_line = raw.strip()
            body_start_idx = idx + 1
            break

    if title_line is None:
        # No non-empty lines at all
        return None, ""

    body_text = "\n".join(lines[body_start_idx:])
    return title_line, body_text


def make_title_from_line(line: str, fallback: str) -> str:
    """
    From something like: 小(xiǎo) 红(hóng) 帽(mào)
    produce: 小红帽
    """
    if not line:
        return fallback
    # Remove pinyin parentheses: 小(xiǎo) 红(hóng) 帽(mào) -> 小 红 帽
    no_pinyin = RUBY_RE.sub(r'\1', line)
    # Remove all whitespace
    title = "".join(no_pinyin.split())
    return title or fallback


def to_ruby_html(text: str) -> str:
    """
    Convert body text to HTML with ruby.
    - Original line breaks -> <p> per non-empty line
    - Half-width spaces are removed
    """

    def repl(match: re.Match) -> str:
        han = match.group(1)
        py = match.group(2)
        return f"<ruby>{han}<rt>{py}</rt></ruby>"

    paragraphs = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Remove half-width spaces
        line = line.replace(" ", "")
        html_line = RUBY_RE.sub(repl, line)
        paragraphs.append(f"<p>{html_line}</p>")

    return "\n\n".join(paragraphs)


def write_story_html(txt_path: pathlib.Path):
    """
    Read one .txt file, write same-name .html, and
    return (html_filename, display_title).
    """
    html_path = txt_path.with_suffix(".html")
    raw_text = txt_path.read_text(encoding="utf-8")

    title_line, body_text = split_title_and_body(raw_text)
    title = make_title_from_line(title_line, txt_path.stem)
    body_html = to_ruby_html(body_text)

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


def main():
    txt_files = sorted(BASE_DIR.glob("*.txt"))
    pages = []

    for txt_path in txt_files:
        html_name, title = write_story_html(txt_path)
        pages.append((html_name, title))

    write_index(pages)


if __name__ == "__main__":
    main()
