#!/usr/bin/env python3
"""Convert content/*.md into static GitHub Pages HTML."""

from pathlib import Path
import re
import markdown

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"

PAGES = {
    "terms-of-service.md": {
        "out": ROOT / "legal" / "terms" / "index.html",
        "title": "Terms of Service — GymDuels",
        "heading": "Terms of Service",
        "link_map": {
            "privacy-policy.md": "../privacy/",
            "terms-of-service.md": "./",
        },
    },
    "privacy-policy.md": {
        "out": ROOT / "legal" / "privacy" / "index.html",
        "title": "Privacy Policy — GymDuels",
        "heading": "Privacy Policy",
        "link_map": {
            "terms-of-service.md": "../terms/",
            "privacy-policy.md": "./",
        },
    },
}

HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="GymDuels {heading}">
  <link rel="stylesheet" href="../../assets/styles.css">
</head>
<body>
  <header class="site-header">
    <div class="site-header__inner">
      <a class="brand" href="../../">GymDuels legal</a>
      <nav class="nav" aria-label="Legal">
        <a href="../terms/">Terms of Service</a>
        <a href="../privacy/">Privacy Policy</a>
      </nav>
    </div>
  </header>
  <main>
    <article class="wrap doc">
"""

FOOTER = """
    </article>
  </main>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <p>Version 2026-07-23</p>
      <p>Last updated: July 23, 2026</p>
    </div>
  </footer>
</body>
</html>
"""


def rewrite_md_links(text: str, link_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        mapped = link_map.get(target)
        if mapped is not None:
            return f"[{label}]({mapped})"
        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, text)


def build_page(src_name: str, meta: dict) -> None:
    raw = (CONTENT / src_name).read_text(encoding="utf-8")
    raw = rewrite_md_links(raw, meta["link_map"])
    # Drop the leading H1 — page chrome already identifies the document.
    raw = re.sub(r"^#\s+.+\n+", "", raw, count=1)
    body = markdown.markdown(
        raw,
        extensions=["tables", "sane_lists"],
        output_format="html5",
    )
    html = (
        HEADER.format(title=meta["title"], heading=meta["heading"])
        + f"      <h1>{meta['heading']}</h1>\n"
        + body
        + FOOTER
    )
    meta["out"].parent.mkdir(parents=True, exist_ok=True)
    meta["out"].write_text(html, encoding="utf-8")
    print(f"wrote {meta['out'].relative_to(ROOT)}")


def main() -> None:
    for src_name, meta in PAGES.items():
        build_page(src_name, meta)


if __name__ == "__main__":
    main()
