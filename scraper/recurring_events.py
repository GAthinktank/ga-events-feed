"""
Recurring annual events with predictable timing.

Each event has a 'season' (month + week-of-month) and a function that
returns the most likely date for a given year. We emit upcoming
occurrences for the current and next year.

If the dates aren't yet officially announced, we mark `confirmed: false`
so the public page can show "(date approximate)".
"""
from datetime import date


def _nth_weekday(year, month, weekday, n):
    """nth occurrence of weekday (Mon=0..Sun=6) in given month."""
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d = date(d.year, d.month, d.day + 1)
    return date(d.year, d.month, d.day + 7 * (n - 1))


# ---- Event templates ----
# Each template: a function that returns (start, end) for a given year.
# Dates are best-known historical patterns; mark confirmed=False so
# the UI can flag them as approximate until the official date is found.

def _munich(year):
    # Mid-February, second or third weekend
    start = _nth_weekday(year, 2, 4, 3)  # 3rd Friday
    return start, date(start.year, start.month, start.day + 2)


def _davos(year):
    # WEF — third or fourth week of January, Mon–Fri
    start = _nth_weekday(year, 1, 0, 3)  # 3rd Monday
    return start, date(start.year, start.month, start.day + 4)


def _g7(year):
    # G7 leaders' summit — typically June, varies by host
    start = date(year, 6, 13)
    return start, date(year, 6, 15)


def _g20(year):
    # G20 leaders' summit — typically November
    start = date(year, 11, 15)
    return start, date(year, 11, 16)


def _nato_summit(year):
    # NATO summit — usually June or July
    start = date(year, 6, 24)
    return start, date(year, 6, 25)


def _unga_hlw(year):
    # UNGA High-Level Week — usually 4th week of September
    start = _nth_weekday(year, 9, 1, 4)  # 4th Tuesday
    return start, date(start.year, start.month, start.day + 4)


def _cop(year):
    # COP — typically November
    start = date(year, 11, 10)
    return start, date(year, 11, 21)


def _aspen(year):
    # Aspen Security Forum — mid-July
    start = date(year, 7, 15)
    return start, date(year, 7, 18)


def _shangri_la(year):
    # Shangri-La Dialogue — early June, Singapore
    start = _nth_weekday(year, 6, 4, 1)  # 1st Friday
    return start, date(start.year, start.month, start.day + 2)


def _halifax(year):
    # Halifax International Security Forum — third weekend November
    start = _nth_weekday(year, 11, 4, 3)  # 3rd Friday
    return start, date(start.year, start.month, start.day + 2)


def _raisina(year):
    # Raisina Dialogue — early March, New Delhi
    start = date(year, 3, 1)
    return start, date(year, 3, 3)


def _doha_forum(year):
    # Doha Forum — early-mid December
    start = date(year, 12, 7)
    return start, date(year, 12, 8)


def _apec(year):
    # APEC Leaders' Meeting — typically mid-November
    start = date(year, 11, 14)
    return start, date(year, 11, 16)


def _brics(year):
    # BRICS Summit — typically July (but varies; Brazil 2025 was July, India 2026 likely Aug-Sep)
    start = date(year, 7, 15)
    return start, date(year, 7, 17)


def _wb_imf_spring(year):
    # World Bank / IMF Spring Meetings — mid-April
    start = date(year, 4, 18)
    return start, date(year, 4, 20)


def _wb_imf_annual(year):
    # World Bank / IMF Annual Meetings — mid-October
    start = date(year, 10, 13)
    return start, date(year, 10, 15)


def _eu_council(year, month):
    """EU Council — quarterly meetings (Mar, Jun, Oct, Dec). Approximate."""
    start = _nth_weekday(year, month, 3, 4)  # 4th Thursday
    return start, date(start.year, start.month, start.day + 1)


# Publication cycles — these are *expected publication windows*, not exact dates.
def _sipri_yearbook(year):  # Mid-June
    return date(year, 6, 15), date(year, 6, 15)


def _iiss_military_balance(year):  # Mid-February
    return date(year, 2, 14), date(year, 2, 14)


def _munich_security_report(year):  # Mid-February, before MSC
    return date(year, 2, 10), date(year, 2, 10)


# ---- Master template list ----
TEMPLATES = [
    # Diplomatic / security summits
    {"key": "msc", "title": "Munich Security Conference",
     "fn": _munich, "location": "Munich, Germany", "organizer": "MSC",
     "region": "EU", "theme": "security", "featured": True,
     "link": "https://securityconference.org/"},
    {"key": "wef", "title": "World Economic Forum (Davos)",
     "fn": _davos, "location": "Davos, Switzerland", "organizer": "WEF",
     "region": "Global", "theme": "economy", "featured": True,
     "link": "https://www.weforum.org/"},
    {"key": "g7", "title": "G7 Leaders' Summit",
     "fn": _g7, "location": "Rotating host country", "organizer": "G7",
     "region": "Global", "theme": "diplomacy", "featured": True,
     "link": ""},
    {"key": "g20", "title": "G20 Leaders' Summit",
     "fn": _g20, "location": "Rotating host country", "organizer": "G20",
     "region": "Global", "theme": "diplomacy", "featured": True,
     "link": ""},
    {"key": "nato", "title": "NATO Summit",
     "fn": _nato_summit, "location": "Rotating host", "organizer": "NATO",
     "region": "Global", "theme": "security", "featured": True,
     "link": "https://www.nato.int/"},
    {"key": "unga", "title": "UN General Assembly — High-Level Week",
     "fn": _unga_hlw, "location": "New York", "organizer": "United Nations",
     "region": "Global", "theme": "diplomacy", "featured": True,
     "link": "https://www.un.org/en/ga/"},
    {"key": "cop", "title": "UN Climate Conference (COP)",
     "fn": _cop, "location": "Rotating host", "organizer": "UNFCCC",
     "region": "Global", "theme": "climate", "featured": True,
     "link": "https://unfccc.int/"},
    {"key": "aspen", "title": "Aspen Security Forum",
     "fn": _aspen, "location": "Aspen, Colorado", "organizer": "Aspen Institute",
     "region": "US", "theme": "security", "featured": False,
     "link": "https://www.aspensecurityforum.org/"},
    {"key": "shangri-la", "title": "Shangri-La Dialogue",
     "fn": _shangri_la, "location": "Singapore", "organizer": "IISS",
     "region": "Asia", "theme": "security", "featured": True,
     "link": "https://www.iiss.org/events/shangri-la-dialogue/"},
    {"key": "halifax", "title": "Halifax International Security Forum",
     "fn": _halifax, "location": "Halifax, Canada", "organizer": "Halifax Forum",
     "region": "Global", "theme": "security", "featured": False,
     "link": "https://halifaxtheforum.org/"},
    {"key": "raisina", "title": "Raisina Dialogue",
     "fn": _raisina, "location": "New Delhi, India", "organizer": "ORF / MEA",
     "region": "IN", "theme": "diplomacy", "featured": False,
     "link": "https://www.orfonline.org/raisina-dialogue/"},
    {"key": "doha", "title": "Doha Forum",
     "fn": _doha_forum, "location": "Doha, Qatar", "organizer": "Qatar MFA",
     "region": "MENA", "theme": "diplomacy", "featured": False,
     "link": "https://dohaforum.org/"},
    {"key": "apec", "title": "APEC Leaders' Meeting",
     "fn": _apec, "location": "Rotating host", "organizer": "APEC",
     "region": "Asia", "theme": "economy", "featured": True,
     "link": "https://www.apec.org/"},
    {"key": "brics", "title": "BRICS Summit",
     "fn": _brics, "location": "Rotating host", "organizer": "BRICS",
     "region": "Global", "theme": "diplomacy", "featured": True,
     "link": ""},
    {"key": "wb-imf-spring", "title": "World Bank / IMF Spring Meetings",
     "fn": _wb_imf_spring, "location": "Washington, DC", "organizer": "WB / IMF",
     "region": "Global", "theme": "economy", "featured": False,
     "link": "https://www.imf.org/"},
    {"key": "wb-imf-annual", "title": "World Bank / IMF Annual Meetings",
     "fn": _wb_imf_annual, "location": "Washington / rotating", "organizer": "WB / IMF",
     "region": "Global", "theme": "economy", "featured": False,
     "link": "https://www.imf.org/"},
    # Annual flagship publications
    {"key": "sipri", "title": "SIPRI Yearbook (publication window)",
     "fn": _sipri_yearbook, "location": "Stockholm", "organizer": "SIPRI",
     "region": "Global", "theme": "security", "featured": False,
     "kind": "publication-cycle",
     "link": "https://www.sipri.org/yearbook"},
    {"key": "iiss-mb", "title": "IISS Military Balance (publication window)",
     "fn": _iiss_military_balance, "location": "London", "organizer": "IISS",
     "region": "Global", "theme": "security", "featured": False,
     "kind": "publication-cycle",
     "link": "https://www.iiss.org/publications/the-military-balance/"},
    {"key": "msc-report", "title": "Munich Security Report (publication window)",
     "fn": _munich_security_report, "location": "Munich", "organizer": "MSC",
     "region": "EU", "theme": "security", "featured": False,
     "kind": "publication-cycle",
     "link": "https://securityconference.org/munich-security-report/"},
]


def generate(today=None, years_ahead=1):
    """Emit recurring events for the current year and `years_ahead` years."""
    today = today or date.today()
    out = []
    for tmpl in TEMPLATES:
        for offset in range(years_ahead + 1):
            year = today.year + offset
            try:
                start, end = tmpl["fn"](year)
            except Exception:
                continue
            # Skip events fully in the past
            if end < today:
                continue
            event = {
                "id": f"{tmpl['key']}-{year}",
                "title": f"{tmpl['title']} {year}",
                "date": start.isoformat(),
                "end_date": end.isoformat(),
                "location": tmpl.get("location", ""),
                "organizer": tmpl.get("organizer", ""),
                "region": tmpl.get("region", ""),
                "theme": tmpl.get("theme", ""),
                "link": tmpl.get("link", ""),
                "summary": "",
                "featured": tmpl.get("featured", False),
                "confirmed": False,    # dates approximate until verified
                "source": "recurring-template",
                "kind": tmpl.get("kind", "diplomatic-event"),
            }
            out.append(event)
    # Quarterly EU Council placeholders for current and next year
    for offset in range(years_ahead + 1):
        year = today.year + offset
        for month in (3, 6, 10, 12):
            start, end = _eu_council(year, month)
            if end < today:
                continue
            out.append({
                "id": f"eu-council-{year}-{month:02d}",
                "title": f"European Council {year}-{month:02d}",
                "date": start.isoformat(),
                "end_date": end.isoformat(),
                "location": "Brussels",
                "organizer": "European Council",
                "region": "EU",
                "theme": "diplomacy",
                "link": "https://www.consilium.europa.eu/",
                "summary": "",
                "featured": False,
                "confirmed": False,
                "source": "recurring-template",
                "kind": "diplomatic-event",
            })
    return out
