"""Crawl the UIU website and build a chunked knowledge base CSV.

Usage:
    python scripts/crawl_uiu.py

Outputs:
    app/rag/data/AskUIU.csv
"""

import os
import re
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "app", "rag", "data", "AskUIU.csv")
BASE_DOMAIN = "uiu.ac.bd"

# Seed URLs covering the most important UIU sections.
SEED_URLS = [
    "https://www.uiu.ac.bd/",
    "https://www.uiu.ac.bd/about-uiu/",
    "https://www.uiu.ac.bd/about-uiu/vision-mission-goals/",
    "https://www.uiu.ac.bd/about-uiu/why-uiu/",
    "https://www.uiu.ac.bd/about-uiu/general-information/",
    "https://www.uiu.ac.bd/about-uiu/uiu-campus/",
    "https://www.uiu.ac.bd/about-uiu/guiding-principles/",
    "https://www.uiu.ac.bd/about-uiu/ranking-accreditation/",
    "https://www.uiu.ac.bd/authorities/",
    "https://www.uiu.ac.bd/authorities/vice-chancellor/",
    "https://www.uiu.ac.bd/authorities/pro-vice-chancellor/",
    "https://www.uiu.ac.bd/authorities/treasurer/",
    "https://www.uiu.ac.bd/authorities/registrar/",
    "https://www.uiu.ac.bd/authorities/dean/",
    "https://www.uiu.ac.bd/authorities/director-of-coordination/",
    "https://www.uiu.ac.bd/admission/",
    "https://www.uiu.ac.bd/admission/undergraduate-program/",
    "https://www.uiu.ac.bd/admission/graduate-program/",
    "https://www.uiu.ac.bd/admission/admission-requirements/",
    "https://www.uiu.ac.bd/admission/admission-procedure/",
    "https://www.uiu.ac.bd/admission/admission-test-procedure/",
    "https://www.uiu.ac.bd/admission/tuition-fees-payment-policies/tuition-fees-waiver/",
    "https://www.uiu.ac.bd/admission/tuition-fees-payment-policies/scholarship-tuition-fee-and-other-fees-waiver-policy/",
    "https://www.uiu.ac.bd/admission/faq/",
    "https://www.uiu.ac.bd/academics/",
    "https://www.uiu.ac.bd/academics/schools-institutes/",
    "https://www.uiu.ac.bd/academics/faculty-members/",
    "https://www.uiu.ac.bd/academics/academic-information-policies/",
    "https://www.uiu.ac.bd/academics/calendar/",
    "https://www.uiu.ac.bd/academics/grading-performance-evaluation/",
    "https://www.uiu.ac.bd/academics/proctorial-committee/",
    "https://www.uiu.ac.bd/academics/probation-policy/",
    "https://www.uiu.ac.bd/research/",
    "https://www.uiu.ac.bd/research/lab-facilities/",
    "https://www.uiu.ac.bd/campus-life/",
    "https://www.uiu.ac.bd/campus-life/sports/",
    "https://www.uiu.ac.bd/campus-life/clubs-forums/",
    "https://www.uiu.ac.bd/campus-life/student-life/",
    "https://www.uiu.ac.bd/health-and-wellness/",
    "https://www.uiu.ac.bd/uiu-transportation-service/",
    "https://www.uiu.ac.bd/contact-us/",
    "https://www.uiu.ac.bd/important-contact/",
    "https://cse.uiu.ac.bd/",
    "https://cse.uiu.ac.bd/about-cse/welcome-message/",
    "https://eee.uiu.ac.bd/",
    "https://eee.uiu.ac.bd/about-eee/welcome-message/",
    "https://ce.uiu.ac.bd/",
    "https://ce.uiu.ac.bd/about-ce/message-from-head/",
    "https://pharmacy.uiu.ac.bd/",
    "https://pharmacy.uiu.ac.bd/about/message-from-the-head/",
    "https://english.uiu.ac.bd/",
    "https://english.uiu.ac.bd/about/message-from-the-head/",
    "https://datascience.uiu.ac.bd/",
    "https://datascience.uiu.ac.bd/about-data-science/welcome-message/",
    "https://sobe.uiu.ac.bd/",
    "https://sobe.uiu.ac.bd/about-sobe/",
]

# URL patterns we explicitly skip.
SKIP_PATTERNS = [
    "/wp-content/",
    "/wp-includes/",
    "/wp-json/",
    "?replytocom=",
    "/author/",
    "/category/",
    "/tag/",
    "/page/",
    "/news/",
    "/notice/",
    "/event/",
    "/gallery/",
    "/uiu_in_media/",
    "/jobs-2/",
    "/profile-login/",
    "/dspace.",
    "/library.",
    "/ucam.",
    "/elms.",
    "/admission.uiu.",
    "/degver.",
    "/admin.uiu.",
]

# Subdomains to include only selectively.
ALLOWED_SUBDOMAINS = {
    "www",
    "cse",
    "eee",
    "ce",
    "pharmacy",
    "english",
    "eds",
    "msj",
    "sobe",
    "datascience",
    "bge",
}

session = requests.Session()
session.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }
)


def is_valid_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if BASE_DOMAIN not in parsed.netloc:
        return False
    subdomain = parsed.netloc.split(".")[0]
    if subdomain not in ALLOWED_SUBDOMAINS:
        return False
    path = parsed.path.lower()
    for pattern in SKIP_PATTERNS:
        if pattern in path or pattern in url.lower():
            return False
    # Skip file downloads.
    if path.endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip")):
        return False
    return True


def normalize_url(url):
    parsed = urlparse(url)
    # Drop query strings and fragments for deduplication.
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def fetch(url):
    try:
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def extract_main_content(html, url):
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements.
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    # Try common WordPress content containers.
    content_selectors = [
        "main#primary",
        "div.entry-content",
        "div.main-content",
        "main",
        "article",
        "div.content-area",
        "div.site-content",
        "body",
    ]
    content_elem = None
    for selector in content_selectors:
        content_elem = soup.select_one(selector)
        if content_elem:
            break

    if not content_elem:
        return title, ""

    # Get paragraphs, headings, list items, and tables.
    text_parts = []
    for elem in content_elem.find_all(["p", "h1", "h2", "h3", "h4", "li", "table"]):
        if elem.name == "table":
            table_lines = []
            for tr in elem.find_all("tr"):
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
                if cells:
                    table_lines.append(" | ".join(cells))
            if table_lines:
                text_parts.append("\n".join(table_lines))
        else:
            text = elem.get_text(" ", strip=True)
            if text:
                text_parts.append(text)

    text = "\n".join(text_parts)
    return title, text


def clean_text(text):
    # Remove excessive whitespace.
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    # Remove very short lines that are likely UI fragments.
    lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 15]
    return "\n".join(lines)


def detect_category(url, title):
    url_lower = url.lower()
    title_lower = title.lower()
    combined = f"{url_lower} {title_lower}"
    if "admission" in combined:
        return "admission"
    if "academic" in combined or "school" in combined or "faculty" in combined:
        return "academics"
    if "tuition" in combined or "scholarship" in combined or "waiver" in combined or "fee" in combined:
        return "fees_scholarships"
    if "campus" in combined or "facility" in combined or "sports" in combined or "club" in combined or "student life" in combined:
        return "campus_life"
    if "research" in combined or "lab" in combined or "institute" in combined or "center" in combined:
        return "research"
    if "contact" in combined or "authority" in combined or "chancellor" in combined or "vice chancellor" in combined:
        return "administration"
    if "about" in combined or "vision" in combined or "mission" in combined or "ranking" in combined:
        return "about"
    return "general"


def chunk_text(text, chunk_size=400, overlap=50):
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks


def discover_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        if is_valid_url(full_url):
            links.add(normalize_url(full_url))
    return links


def crawl(max_pages=80):
    to_visit = [normalize_url(url) for url in SEED_URLS]
    visited = set()
    pages = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        print(f"[{len(visited)}/{max_pages}] Crawling {url}")
        html = fetch(url)
        if not html:
            continue

        title, raw_text = extract_main_content(html, url)
        text = clean_text(raw_text)
        if not text or len(text.split()) < 30:
            # Page has too little content; still discover links but skip storing.
            new_links = discover_links(html, url)
            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
            continue

        category = detect_category(url, title)
        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            pages.append(
                {
                    "Title": title,
                    "Source": url,
                    "Category": category,
                    "ChunkIndex": idx,
                    "Text": chunk,
                    "LastCrawled": datetime.now(timezone.utc).isoformat(),
                }
            )

        new_links = discover_links(html, url)
        for link in new_links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

        time.sleep(0.5)

    return pages


def main():
    print("Starting UIU website crawl...")
    pages = crawl(max_pages=80)
    print(f"Crawled {len(pages)} chunks from {len(set(p['Source'] for p in pages))} pages.")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = pd.DataFrame(pages)
    # Ensure Text column is first for backward compatibility.
    cols = ["Text"] + [c for c in df.columns if c != "Text"]
    df = df[cols]
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved knowledge base to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
