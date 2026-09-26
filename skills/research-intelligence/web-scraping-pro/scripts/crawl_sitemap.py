#!/usr/bin/env python3
"""Sitemap XML Crawler and URL Extractor.

Parses sitemaps and sitemap index files to discover all indexed URLs of a competitor.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET


def fetch_sitemap(url: str) -> list[str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        xml_content = resp.read()

    root = ET.fromstring(xml_content)
    # Handle namespace if present
    namespace = ""
    match = re.match(r"\{.*\}", root.tag)
    if match:
        namespace = match.group(0)

    urls = []
    # Check if sitemap index
    sitemaps = root.findall(f"{namespace}sitemap")
    if sitemaps:
        for s in sitemaps:
            loc = s.find(f"{namespace}loc")
            if loc is not None and loc.text:
                urls.extend(fetch_sitemap(loc.text.strip()))
    else:
        for url_node in root.findall(f"{namespace}url"):
            loc = url_node.find(f"{namespace}loc")
            if loc is not None and loc.text:
                urls.append(loc.text.strip())

    return sorted(list(set(urls)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae todas las URLs de un sitemap.xml")
    parser.add_argument("sitemap_url", help="URL del sitemap.xml")
    parser.add_argument("-o", "--output", help="Archivo de texto de salida")
    args = parser.parse_args()

    try:
        urls = fetch_sitemap(args.sitemap_url)
        print(f"✔ Se encontraron {len(urls)} URLs en {args.sitemap_url}", file=sys.stderr)
        out_content = "\n".join(urls) + "\n"
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out_content)
            print(f"✔ URLs guardadas en {args.output}", file=sys.stderr)
        else:
            print(out_content)
    except Exception as exc:
        print(f"Error al procesar sitemap: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
