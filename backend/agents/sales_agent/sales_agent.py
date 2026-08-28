# backend/agents/sales_agent/sales_agent.py

"""
Sales Agent (Worker Agent)

Per the brief, the Sales Agent:
  1. Scans a set of predefined URLs to identify RFPs due for submission in
     the next 3 months.
  2. Summarizes the RFPs found, with their due dates.
  3. Identifies exactly one RFP to respond to and hands it to the Main Agent.

This is deliberately built as plain HTML parsing (BeautifulSoup + regex) with
no LLM call anywhere in the path - the client's own data says late discovery
is the single biggest driver of lost bids, so the identification step needs
to be cheap and fast enough to run continuously, not gated on model latency
or quota. The predefined URLs point at local mock tender-listing pages
(backend/mock_portals/) standing in for real LSTK-executor / e-procurement
sites, per the challenge's data assumptions. Swapping in real URLs later is
just a config change - _fetch_html already handles http(s) as well as local
files.
"""

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent  # backend/
MOCK_PORTALS_DIR = PROJECT_ROOT / "mock_portals"
SAMPLES_DIR = PROJECT_ROOT / "samples"

# Predefined URLs the Sales Agent scans. In production these would be real
# LSTK-executor tender portals / e-procurement sites; here they're local
# mock pages so identification is demoable without live scraping or an API key.
PREDEFINED_URLS = [
    str(MOCK_PORTALS_DIR / "portal_a_infra_tenders.html"),
    str(MOCK_PORTALS_DIR / "portal_b_psu_etender.html"),
    str(MOCK_PORTALS_DIR / "portal_c_gov_notices.html"),
]

# Simple product-fit keyword gate: the client only wants wires/cables RFPs,
# not every tender that happens to fall in the 3-month window (e.g. a
# flyover steel tender should be found but not selected for response).
QUALIFYING_KEYWORDS = [
    "cable", "wire", "conductor", "armoured", "armored",
    "pijf", "frls", "telecom cable", "power cable",
]

DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%d %B %Y", "%d %b %Y")


def _fetch_html(source: str) -> str:
    parsed = urlparse(source)
    if parsed.scheme in ("http", "https"):
        resp = requests.get(source, timeout=15)
        resp.raise_for_status()
        return resp.text
    return Path(source).read_text(encoding="utf-8")


def _parse_deadline(raw: str) -> Optional[date]:
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    match = re.search(r"\d{4}-\d{2}-\d{2}", raw)
    if match:
        return datetime.strptime(match.group(0), "%Y-%m-%d").date()
    return None


class SalesAgent:
    """Identifies RFPs due within the response window and picks one to escalate."""

    def __init__(self, urls: Optional[List[str]] = None, lookahead_days: int = 90):
        self.urls = urls or PREDEFINED_URLS
        self.lookahead_days = lookahead_days

    # -----------------------------------------------------
    # STEP 1: SCAN URLS
    # -----------------------------------------------------
    def scan_urls(self) -> List[Dict[str, Any]]:
        entries = []
        for url in self.urls:
            try:
                html = _fetch_html(url)
            except Exception as exc:
                print(f"WARNING: failed to fetch {url}: {exc}")
                continue
            entries.extend(self._parse_portal(html, source=url))
        return entries

    def _parse_portal(self, html: str, source: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")

        structured_nodes = soup.select("[data-rfp-id]")
        if structured_nodes:
            entries = [self._parse_structured_node(n, source) for n in structured_nodes]
        else:
            entries = self._parse_unstructured(soup, source)

        return [e for e in entries if e is not None]

    def _parse_structured_node(self, node, source: str) -> Optional[Dict[str, Any]]:
        deadline = _parse_deadline(node.get("data-deadline", ""))
        if deadline is None:
            return None
        return {
            "rfp_id": node.get("data-rfp-id", "").strip(),
            "title": node.get("data-title", "").strip(),
            "issuing_authority": node.get("data-authority", "").strip(),
            "deadline": deadline.isoformat(),
            "product_keywords": [
                k.strip() for k in node.get("data-keywords", "").split(",") if k.strip()
            ],
            "pdf_file": node.get("data-pdf", "").strip(),
            "source_url": source,
        }

    def _parse_unstructured(self, soup: BeautifulSoup, source: str) -> List[Dict[str, Any]]:
        """
        Fallback for legacy notice-board style pages with no structured
        markup: each tender is a free-text <li>/<p> block, e.g.
        "RFP No: X - <description>. Document: <file>. Due: <date>"
        """
        entries = []
        for block in soup.select("li, p"):
            text = " ".join(block.get_text(" ", strip=True).split())

            due_match = re.search(r"Due:\s*(\d{4}-\d{2}-\d{2})", text, re.I)
            if not due_match:
                continue
            deadline = _parse_deadline(due_match.group(1))
            if deadline is None:
                continue

            id_match = re.search(r"(?:RFP|Tender)\s*No\.?:?\s*([A-Z0-9\-/]+)", text, re.I)
            rfp_id = id_match.group(1) if id_match else text[:20]

            doc_match = re.search(r"Document:\s*([\w\-]+\.pdf|none)", text, re.I)
            pdf_file = ""
            if doc_match and doc_match.group(1).lower() != "none":
                pdf_file = doc_match.group(1)

            title = text.split(id_match.group(0), 1)[-1] if id_match else text
            title = re.split(r"—|-", title, maxsplit=1)[-1]
            title = re.split(r"\s*Document:", title)[0].strip()

            entries.append({
                "rfp_id": rfp_id,
                "title": title[:150],
                "issuing_authority": "",
                "deadline": deadline.isoformat(),
                "product_keywords": [],
                "pdf_file": pdf_file,
                "source_url": source,
            })
        return entries

    # -----------------------------------------------------
    # STEP 2: QUALIFY (due within next 3 months + product fit)
    # -----------------------------------------------------
    def qualify(
        self, entries: List[Dict[str, Any]], today: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        today = today or date.today()
        horizon = today + timedelta(days=self.lookahead_days)

        qualified = []
        for e in entries:
            deadline = date.fromisoformat(e["deadline"])
            if deadline < today or deadline > horizon:
                continue

            text_blob = " ".join([e["title"], " ".join(e["product_keywords"])]).lower()
            matched_keywords = [k for k in QUALIFYING_KEYWORDS if k in text_blob]

            qualified.append({
                **e,
                "days_remaining": (deadline - today).days,
                "matched_keywords": matched_keywords,
                "product_fit": bool(matched_keywords),
            })

        return sorted(qualified, key=lambda x: x["days_remaining"])

    # -----------------------------------------------------
    # STEP 3: SELECT ONE RFP FOR RESPONSE
    # -----------------------------------------------------
    def select_rfp(self, qualified: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Among RFPs due in the window, prefer ones matching the client's
        wires/cables product scope, then pick the most urgent (earliest
        deadline) - the client's own data shows on-time action is the
        strongest predictor of a win, so "urgent and in-scope" beats
        "later but in-scope". Falls back to the earliest deadline overall
        if nothing matches the product scope.
        """
        candidates = [e for e in qualified if e["product_fit"]] or qualified
        return candidates[0] if candidates else None

    # -----------------------------------------------------
    # FULL RUN
    # -----------------------------------------------------
    def run(self, today: Optional[date] = None) -> Dict[str, Any]:
        raw_entries = self.scan_urls()
        qualified = self.qualify(raw_entries, today=today)
        selected = self.select_rfp(qualified)

        selected_pdf_path = None
        if selected and selected.get("pdf_file"):
            candidate = SAMPLES_DIR / selected["pdf_file"]
            if candidate.exists():
                selected_pdf_path = str(candidate)

        return {
            "scanned_urls": self.urls,
            "total_rfps_found": len(raw_entries),
            "rfps_due_in_window": qualified,
            "selected_rfp": selected,
            "selected_rfp_pdf_path": selected_pdf_path,
        }


if __name__ == "__main__":
    result = SalesAgent().run()
    print(json.dumps(result, indent=2))
