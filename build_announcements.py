"""Build new bilingual announcements from one Markdown file per item.

The existing archive is read from the published HTML, preserving its current
content and styling. New content lives in content/announcements/*.md. Running
this script creates both detail pages and refreshes both home/archive lists.
"""

from __future__ import annotations

import html as html_entities
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml
from lxml import etree, html

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
CONTENT = ROOT / "content" / "announcements"
ARTICLE_TEMPLATE = "2026-07-06-bioimageit-v2-manuscript"


def read_markdown(path: Path) -> dict:
    source = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"---\s*\n(.*?)\n---\s*\n(.*)", source, re.S)
    if not match:
        raise ValueError(f"{path.name}: expected YAML front matter between --- lines")
    fields = yaml.safe_load(match.group(1))
    if not isinstance(fields, dict):
        raise ValueError(f"{path.name}: front matter must contain fields")
    for field in ("date", "title_en", "title_zh", "summary_en", "summary_zh", "category"):
        if not fields.get(field):
            raise ValueError(f"{path.name}: missing {field}")
    # YAML may parse ISO dates as date objects; both types are accepted.
    when = date.fromisoformat(str(fields["date"]))
    slug = path.stem
    if not slug.startswith(when.isoformat() + "-"):
        raise ValueError(f"{path.name}: filename must start with {when.isoformat()}-")
    sections = re.split(r"(?m)^## (English|中文)\s*$", match.group(2))
    bodies = {}
    for i in range(1, len(sections), 2):
        bodies[sections[i]] = sections[i + 1].strip()
    if not bodies.get("English") or not bodies.get("中文"):
        raise ValueError(f"{path.name}: provide ## English and ## 中文 body sections")
    fields.update(slug=slug, date=when, bodies=bodies)
    return fields


def markdown_paragraphs(body: str) -> list[str]:
    """Render plain Markdown paragraphs and links without allowing raw HTML."""
    result = []
    for paragraph in re.split(r"\n\s*\n", body):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        escaped = html_entities.escape(" ".join(paragraph.split()))
        escaped = re.sub(
            r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
            lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>',
            escaped,
        )
        result.append(escaped)
    return result


def read_archive(language: str) -> dict[str, dict]:
    base = DIST / ("zh" if language == "zh" else "")
    tree = html.fromstring((base / "announcements" / "index.html").read_text(encoding="utf-8"))
    records = {}
    for link in tree.xpath("//a[contains(concat(' ',normalize-space(@class),' '),' announcement ')]"):
        slug = link.get("href", "").rstrip("/").split("/")[-1]
        time = link.xpath("./time[@datetime]")
        title = link.xpath("./div/strong")
        summary = link.xpath("./div/span[not(contains(@class,'category'))]")
        category = link.xpath("./div/span[contains(@class,'category')]")
        if time and title and summary and category:
            records[slug] = {
                "slug": slug,
                "date": date.fromisoformat(time[0].get("datetime")[:10]),
                "title": title[0].text_content().removesuffix("→").strip(),
                "summary": summary[-1].text_content().strip(),
                "category": category[0].text_content().strip(),
            }
    return records


def format_date(when: date, language: str) -> str:
    return f"{when.year}年{when.month}月{when.day}日" if language == "zh" else f"{when.day} {when.strftime('%B')} {when.year}"


def make_entry(record: dict, language: str):
    slug = record["slug"]
    prefix = "/zh" if language == "zh" else ""
    link = html.Element("a", {"class": "announcement", "href": f"{prefix}/announcements/{slug}/"})
    time = etree.SubElement(link, "time", datetime=record["date"].isoformat())
    time.text = format_date(record["date"], language)
    inner = etree.SubElement(link, "div")
    label = etree.SubElement(inner, "span", {"class": "category"})
    label.text = record["category"]
    title = etree.SubElement(inner, "strong")
    title.text = record["title"].rstrip(" →") + " →"
    summary = etree.SubElement(inner, "span")
    summary.text = record["summary"]
    return link


def replace_list(container, records: list[dict], language: str):
    for child in list(container):
        container.remove(child)
    for item in records:
        container.append(make_entry(item, language))


def save_tree(path: Path, tree):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<!doctype html>\n" + html.tostring(tree, encoding="unicode", method="html"), encoding="utf-8")


def refresh_lists(records: dict[str, dict], language: str):
    base = DIST / ("zh" if language == "zh" else "")
    items = sorted(records.values(), key=lambda r: (r["date"], r["slug"]), reverse=True)
    home_path = base / "index.html"
    home = html.fromstring(home_path.read_text(encoding="utf-8"))
    home_list = home.xpath("//section[@id='announcements']//div[contains(@class,'announcements-list')]")[0]
    replace_list(home_list, items[:4], language)
    save_tree(home_path, home)

    archive_path = base / "announcements" / "index.html"
    archive = html.fromstring(archive_path.read_text(encoding="utf-8"))
    layout = archive.xpath("//main//div[contains(@class,'page-layout')]")[0]
    for element in list(layout):
        if element.get("class", "") in ("archive-year", "announcements-list"):
            layout.remove(element)
    by_year = defaultdict(list)
    for item in items:
        by_year[item["date"].year].append(item)
    for year, group in sorted(by_year.items(), reverse=True):
        heading = etree.SubElement(layout, "h2", {"class": "archive-year"})
        heading.text = str(year)
        listing = etree.SubElement(layout, "div", {"class": "announcements-list"})
        replace_list(listing, group, language)
    save_tree(archive_path, archive)


def make_article(item: dict, language: str, all_records: dict[str, dict]):
    base = DIST / ("zh" if language == "zh" else "")
    template = base / "announcements" / ARTICLE_TEMPLATE / "index.html"
    tree = html.fromstring(template.read_text(encoding="utf-8"))
    slug = item["slug"]
    is_chinese = language == "zh"
    tree.xpath("//head/title")[0].text = f"{item['title_zh' if is_chinese else 'title_en']} · Cesar Valades-Cruz"
    desc = tree.xpath("//head/meta[@name='description']")
    if desc:
        desc[0].set("content", item["summary_zh" if is_chinese else "summary_en"])
    hero = tree.xpath("//main//section[contains(@class,'page-hero')]//div[contains(@class,'shell')]")[0]
    eyebrow = hero.xpath("./p[contains(@class,'eyebrow')]")[0]
    category = ("预印本" if item["category"].lower() == "preprints" else "论文发表" if item["category"].lower() == "manuscripts" else item.get("category_zh", "科研动态")) if is_chinese else item["category"]
    eyebrow.text = format_date(item["date"], language) + " · " + category
    hero.xpath("./h1")[0].text = item["title_zh" if is_chinese else "title_en"]
    hero.xpath("./p[not(contains(@class,'eyebrow'))]")[0].text = item["summary_zh" if is_chinese else "summary_en"]

    section = tree.xpath("//section[contains(@class,'pub-announcement')]")[0]
    section.xpath(".//p[contains(@class,'pub-intro')]")[0].text = item["summary_zh" if is_chinese else "summary_en"]
    for existing in section.xpath(".//p[contains(@class,'pub-description')]"):
        existing.drop_tree()
    for paragraph in markdown_paragraphs(item["bodies"]["中文" if is_chinese else "English"]):
        fragment = html.fragment_fromstring(f'<p class="pub-description">{paragraph}</p>')
        section.append(fragment)
    for el in section.xpath(".//div[contains(@class,'pub-resources')]|.//div[contains(@class,'pub-collab')]"):
        el.drop_tree()
    card = section.xpath(".//div[contains(@class,'pub-card') and not(contains(@class,'pub-card-'))]")
    if item.get("paper_url") and item.get("paper_title"):
        if card:
            card = card[0]
            journal = card.xpath(".//div[contains(@class,'pub-journal')]")
            if journal:
                journal[0].text = item.get("journal", "Publication")
            title = card.xpath(".//h2")
            if title:
                title[0].text = item["paper_title"]
            authors = card.xpath(".//p[contains(@class,'pub-authors')]")
            if authors:
                authors[0].text = item.get("authors", "")
            links = card.xpath(".//a")
            if links:
                links[0].set("href", item["paper_url"])
                links[0].text = "阅读论文 ↗" if is_chinese else "Read the paper ↗"
            metadata = card.xpath(".//div[contains(@class,'pub-meta')]")
            if metadata:
                metadata[0].text = format_date(item["date"], language)
    else:
        for el in card:
            el.drop_tree()
    previous = [r for r in sorted(all_records.values(), key=lambda r:r["date"], reverse=True) if r["date"] < item["date"]]
    links = tree.xpath("//main//div[contains(@class,'page-layout')]/p[last()]/a")
    if len(links) > 1:
        if previous:
            prefix = "/zh" if is_chinese else ""
            links[1].set("href", f"{prefix}/announcements/{previous[0]['slug']}/")
        else:
            links[1].drop_tree()
    save_tree(base / "announcements" / slug / "index.html", tree)


def main():
    english = read_archive("en")
    chinese = read_archive("zh")
    authored = [read_markdown(p) for p in sorted(CONTENT.glob("*.md")) if not p.name.startswith("_")]
    if not authored:
        print("No new announcements; existing pages are unchanged.")
        return
    for item in authored:
        slug = item["slug"]
        for language, records in (("en", english), ("zh", chinese)):
            records[slug] = {
                "slug": slug,
                "date": item["date"],
                "title": item["title_zh" if language == "zh" else "title_en"],
                "summary": item["summary_zh" if language == "zh" else "summary_en"],
                "category": ("预印本" if item["category"].lower() == "preprints" else "论文发表" if item["category"].lower() == "manuscripts" else item.get("category_zh", "科研动态")) if language == "zh" else item["category"],
            }
    for item in authored:
        make_article(item, "en", english)
        make_article(item, "zh", chinese)
    for language, records in (("en", english), ("zh", chinese)):
        refresh_lists(records, language)
    print(f"Built {len(authored)} authored announcements and refreshed both language indexes.")


if __name__ == "__main__":
    main()
