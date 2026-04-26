"""
Main scraper. Fetches all RSS/Atom feeds, normalizes entries,
applies filters, detects events from publications, and merges with
recurring event templates.

Outputs three JSON files:
  data/publications.json       (strict-filtered, public)
  data/publications-all.json   (everything except noise, for admin/audit)
  data/calendar.json           (events: detected + recurring + manual)
"""
import json
import hashlib
import re
import sys
import time
import traceback
from datetime import datetime, date, timezone
from pathlib import Path

import feedparser
import requests
import yaml
from dateutil import parser as dtparser

from sources import SOURCES
from filters import (
    is_noise, is_strict, detect_theme, detect_region_hint, STRICT_RE,
)
from recurring_events import generate as generate_recurring

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

USER_AGENT = "GA-ThinkTank-EventsBot/2.0 (+https://gathinktank.com)"
TIMEOUT = 25
MAX_PER_SOURCE = 25  # cap entries per feed to avoid noise floods

# Patterns to detect an event date inside a press-release title or summary,
# e.g. "Foreign Affairs Council on 12 March 2026" / "12-13 mars 2026"
EVENT_DATE_PATTERNS = [
    r"\b(\d{1,2})[\.\-– ]+(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december|janvier|février|fevrier|mars|avril|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre|januar|februar|märz|maerz|juni|juli|oktober|dezember|enero|febrero|marzo|junio|julio|septiembre|octubre|noviembre|diciembre|gennaio|febbraio|aprile|maggio|giugno|luglio|settembre|ottobre|dicembre)\s+(\d{4})\b",
    r"\b(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})\b",
    r"\b(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})\b",
    r"\b(\d{1,2})\.\s*(januar|februar|märz|maerz|april|mai|juni|juli|august|september|oktober|november|dezember)\s+(\d{4})\b",
    r"\b(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})\b",
    r"\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b",
    r"\b(\d{4})-(\d{2})-(\d{2})\b",
]
EVENT_DATE_RE = re.compile("|".join(EVENT_DATE_PATTERNS), re.IGNORECASE)

# Words that indicate "this is an event, not a paper"
EVENT_INDICATORS = re.compile(
    r"\b(meet(ing|s)|summit|conference|forum|council|dialogue|hosts?|"
    r"r[eé]union|conseil|sommet|conf[eé]rence|"
    r"treffen|gipfel|tagung|"
    r"reuni[oó]n|cumbre|conferencia|"
    r"riunione|vertice|conferenza|"
    r"vergadering|top|conferentie)\b",
    re.IGNORECASE,
)


def normalize_text(s):
    if not s:
        return ""
    # Strip HTML tags crudely
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def make_id(*parts):
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return h


def parse_entry_date(entry):
    for key in ("published", "updated", "created"):
        v = entry.get(key) or entry.get(key + "_parsed")
        if not v:
            continue
        if isinstance(v, str):
            try:
                return dtparser.parse(v, fuzzy=True).date()
            except Exception:
                pass
        elif hasattr(v, "tm_year"):
            try:
                return date(v.tm_year, v.tm_mon, v.tm_mday)
            except Exception:
                pass
    return None


def fetch_feed(source):
    """Returns a list of normalized entries, or [] on error."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"}
    try:
        r = requests.get(source["url"], headers=headers, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code != 200:
            print(f"  ✗ HTTP {r.status_code} from {source['name']}", file=sys.stderr)
            return []
        # Use bytes so feedparser handles encoding
        feed = feedparser.parse(r.content)
    except Exception as e:
        print(f"  ✗ {source['name']}: {e}", file=sys.stderr)
        return []

    if feed.bozo and not getattr(feed, "entries", None):
        print(f"  ✗ {source['name']}: malformed feed ({feed.bozo_exception})", file=sys.stderr)
        return []

    entries = []
    for raw in feed.entries[:MAX_PER_SOURCE]:
        title = normalize_text(raw.get("title", ""))
        if not title:
            continue
        link = raw.get("link") or ""
        summary = normalize_text(raw.get("summary") or raw.get("description") or "")
        pubdate = parse_entry_date(raw)

        text = f"{title} {summary}"
        if is_noise(text):
            continue

        # Region: source default, but override if a strong country hint appears
        # in the text (Russia/China/India). This is what catches "EEAS on Russia."
        region = source["region"]
        hint = detect_region_hint(text)
        if hint and source["type"] != "gov":
            # Only override for non-government sources, since gov region IS the source
            region = hint

        theme = detect_theme(text)

        item = {
            "id": make_id(source["name"], title, link),
            "title": title,
            "summary": summary[:600] if summary else "",
            "link": link,
            "date": pubdate.isoformat() if pubdate else None,
            "source": source["name"],
            "source_type": source["type"],
            "region": region,
            "lang": source["lang"],
            "theme": theme,
        }
        entries.append(item)
    return entries


def extract_event_from_entry(entry):
    """If the entry text contains an event date and event indicator,
    emit a calendar event. Returns dict or None."""
    text = f"{entry['title']} {entry.get('summary','')}"
    if not EVENT_INDICATORS.search(text):
        return None

    # Try the regex patterns in order until one matches
    m = EVENT_DATE_RE.search(text)
    if not m:
        return None

    # Try to coerce the matched substring into a date via dateutil
    matched = m.group(0)
    try:
        # dateutil handles many languages via fuzzy parse
        parsed = dtparser.parse(matched, fuzzy=True, dayfirst=True)
    except Exception:
        return None

    today = date.today()
    if parsed.date() < today:
        return None  # past event

    # Calendar event derived from a publication
    return {
        "id": entry["id"] + "-evt",
        "title": entry["title"],
        "date": parsed.date().isoformat(),
        "end_date": parsed.date().isoformat(),
        "location": "",
        "organizer": entry["source"],
        "region": entry["region"],
        "theme": entry.get("theme") or "diplomacy",
        "link": entry["link"],
        "summary": entry.get("summary", "")[:300],
        "featured": False,
        "confirmed": True,
        "source": entry["source"],
        "kind": "diplomatic-event",
        "lang": entry["lang"],
    }


def load_manual_yaml(filename, key):
    p = ROOT / filename
    if not p.exists():
        return []
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or []
        if not isinstance(data, list):
            return []
        return data
    except Exception as e:
        print(f"  ! {filename}: {e}", file=sys.stderr)
        return []


def main():
    started = datetime.now(timezone.utc)
    print(f"=== GA Events Feed scrape — {started.isoformat()} ===")
    print(f"Sources: {len(SOURCES)}")

    all_pubs = []
    public_pubs = []
    detected_events = []
    stats = {"ok": 0, "fail": 0, "items_total": 0, "items_strict": 0, "events_detected": 0}

    for src in SOURCES:
        print(f"→ {src['name']} ({src['region']}, {src['lang']})")
        entries = fetch_feed(src)
        if not entries:
            stats["fail"] += 1
            continue
        stats["ok"] += 1
        stats["items_total"] += len(entries)

        for e in entries:
            all_pubs.append(e)

            # Strict filter for public feed
            text = f"{e['title']} {e.get('summary','')}"
            if is_strict(text):
                public_pubs.append(e)
                stats["items_strict"] += 1

            # Try to extract event
            evt = extract_event_from_entry(e)
            if evt:
                detected_events.append(evt)
                stats["events_detected"] += 1

        time.sleep(0.5)  # be gentle to servers

    # Sort publications by date desc, fallback to title
    def sort_key(p):
        return (p.get("date") or "0000-00-00", p["title"])
    all_pubs.sort(key=sort_key, reverse=True)
    public_pubs.sort(key=sort_key, reverse=True)

    # ==== Calendar: recurring + detected + manual ====
    recurring = generate_recurring()
    manual = load_manual_yaml("manual_events.yml", "events")
    excludes = set(load_manual_yaml("manual_excludes.yml", "ids"))

    # Normalize manual events to the same shape; manual entries override featured/etc.
    manual_normalized = []
    for m in manual:
        if not m.get("title") or not m.get("date"):
            continue
        manual_normalized.append({
            "id": m.get("id") or make_id("manual", m["title"], str(m["date"])),
            "title": m["title"],
            "date": str(m["date"]),
            "end_date": str(m.get("end_date") or m["date"]),
            "location": m.get("location", ""),
            "organizer": m.get("organizer", ""),
            "region": m.get("region", "Global"),
            "theme": m.get("theme", ""),
            "link": m.get("link", ""),
            "summary": m.get("summary", ""),
            "featured": bool(m.get("featured", False)),
            "confirmed": True,
            "source": "manual",
            "kind": m.get("kind", "diplomatic-event"),
        })

    # Merge: manual > recurring > detected (later overwrites earlier on duplicate IDs).
    by_id = {}
    for evt in detected_events + recurring + manual_normalized:
        if evt["id"] in excludes:
            continue
        # If a recurring event matches a manual entry by approximate title+year,
        # prefer the manual one.
        by_id[evt["id"]] = evt

    calendar = list(by_id.values())
    calendar.sort(key=lambda e: e["date"])

    # ==== Write outputs ====
    finished = datetime.now(timezone.utc)
    meta = {
        "generated_at": finished.isoformat(),
        "duration_seconds": (finished - started).total_seconds(),
        "stats": stats,
        "source_count": len(SOURCES),
    }

    (DATA_DIR / "publications.json").write_text(
        json.dumps({"meta": meta, "items": public_pubs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (DATA_DIR / "publications-all.json").write_text(
        json.dumps({"meta": meta, "items": all_pubs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (DATA_DIR / "calendar.json").write_text(
        json.dumps({"meta": meta, "items": calendar}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print()
    print("=" * 50)
    print(f"Sources OK / fail : {stats['ok']} / {stats['fail']}")
    print(f"Items total       : {stats['items_total']}")
    print(f"Strict-filtered   : {stats['items_strict']}")
    print(f"Events detected   : {stats['events_detected']}")
    print(f"Recurring events  : {len(recurring)}")
    print(f"Manual events     : {len(manual_normalized)}")
    print(f"Calendar total    : {len(calendar)}")
    print(f"Duration          : {meta['duration_seconds']:.1f}s")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
