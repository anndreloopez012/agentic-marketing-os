#!/usr/bin/env python3
"""HTML to Clean Markdown Scraper.

Converts any public webpage into clean, structured Markdown suitable for
LLM analysis and competitive intelligence, without requiring third-party deps.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.request
from datetime import datetime
from html.parser import HTMLParser


class SimpleMarkdownExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.in_title = False
        self.meta_desc = ""
        self.output: list[str] = []
        self.ignore_tags = {"script", "style", "nav", "footer", "header", "aside", "noscript", "svg"}
        self.ignore_depth = 0
        self.heading_level = 0
        self.in_link = False
        self.link_url = ""
        self.in_list_item = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_lower = tag.lower()
        if tag_lower in self.ignore_tags:
            self.ignore_depth += 1
            return

        if self.ignore_depth > 0:
            return

        attrs_dict = {k.lower(): v for k, v in attrs if v is not None}

        if tag_lower == "title":
            self.in_title = True
        elif tag_lower == "meta" and attrs_dict.get("name", "").lower() in ("description", "og:description"):
            self.meta_desc = attrs_dict.get("content", "")
        elif re.match(r"^h([1-6])$", tag_lower):
            self.heading_level = int(tag_lower[1])
            self.output.append(f"\n\n{'#' * self.heading_level} ")
        elif tag_lower == "p":
            self.output.append("\n\n")
        elif tag_lower == "br":
            self.output.append("\n")
        elif tag_lower == "li":
            self.in_list_item = True
            self.output.append("\n- ")
        elif tag_lower == "a":
            href = attrs_dict.get("href", "")
            if href and not href.startswith("javascript:"):
                self.in_link = True
                self.link_url = href
                self.output.append("[")

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower in self.ignore_tags:
            if self.ignore_depth > 0:
                self.ignore_depth -= 1
            return

        if self.ignore_depth > 0:
            return

        if tag_lower == "title":
            self.in_title = False
        elif re.match(r"^h([1-6])$", tag_lower):
            self.heading_level = 0
            self.output.append("\n")
        elif tag_lower == "a" and self.in_link:
            self.output.append(f"]({self.link_url})")
            self.in_link = False
            self.link_url = ""
        elif tag_lower == "li":
            self.in_list_item = False

    def handle_data(self, data: str) -> None:
        if self.ignore_depth > 0:
            return

        clean_text = re.sub(r"\s+", " ", data)
        if self.in_title:
            self.title += clean_text
        elif clean_text.strip():
            self.output.append(clean_text)


def scrape_url(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        raw_html = resp.read().decode(charset, errors="replace")

    parser = SimpleMarkdownExtractor()
    parser.feed(raw_html)

    body = "".join(parser.output).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    frontmatter = [
        "---",
        f"url: \"{url}\"",
        f"title: \"{html.unescape(parser.title.strip())}\"",
        f"description: \"{html.unescape(parser.meta_desc.strip())}\"",
        f"scraped_at: \"{timestamp}\"",
        "---",
        "",
        body,
    ]
    return "\n".join(frontmatter)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae contenido de una URL y lo convierte a Markdown limpio.")
    parser.add_argument("url", help="URL a extraer")
    parser.add_argument("-o", "--output", help="Ruta de archivo de salida (por defecto: stdout)")
    args = parser.parse_args()

    try:
        md = scrape_url(args.url)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"✔ Contenido guardado en {args.output}", file=sys.stderr)
        else:
            print(md)
    except Exception as exc:
        print(f"Error al extraer {args.url}: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
