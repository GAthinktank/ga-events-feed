# GA! Events Feed

Auto-updating feed of international affairs publications and events,
serving the GA! Think Tank website (gathinktank.com).

## How it works

1. **GitHub Actions** runs `scraper/main.py` every 6 hours (and on every push).
2. The scraper fetches ~80 RSS feeds from governments, IOs, and think tanks across Europe, US, UK, Russia, India, China, Japan, Korea, Australia, Africa, Latin America.
3. It outputs three JSON files into `data/`:
   - `publications.json` — strict-filtered (strategy papers, white papers, doctrines, communiqués). **This is what the public WordPress page reads.**
   - `publications-all.json` — full unfiltered feed (for admin/audit).
   - `calendar.json` — events: hardcoded recurring summits + auto-detected ad-hoc events from press releases + manually-added events from `manual_events.yml`.
4. Anyone can fetch these JSON files at:
   - `https://raw.githubusercontent.com/GAthinktank/ga-events-feed/main/data/calendar.json`
   - `https://raw.githubusercontent.com/GAthinktank/ga-events-feed/main/data/publications.json`

## Adding a new event

Edit [`manual_events.yml`](manual_events.yml) directly on GitHub.com (use the pencil icon). Add:

```yaml
- title: "Munich Security Conference 2027"
  date: 2027-02-12
  end_date: 2027-02-14
  location: "Munich, Germany"
  region: EU
  theme: security
  link: "https://securityconference.org/"
  featured: true
```

Commit. The next push automatically re-runs the scraper, which will include your event in `calendar.json` within ~1 minute.

## Hiding a false-positive event

If the scraper detects something it shouldn't, find its ID in `data/calendar.json`, then add it to [`manual_excludes.yml`](manual_excludes.yml). Commit. Done.

## Adding/removing a source

Edit [`scraper/sources.py`](scraper/sources.py). Each source is one line. Commit.

## Running the scraper now (instead of waiting 6h)

GitHub Actions tab → "Refresh feeds" → "Run workflow" → "Run workflow" button.

## Architecture

```
ga-events-feed/
├── .github/workflows/scrape.yml    # Runs every 6h
├── scraper/
│   ├── main.py                     # Entry point
│   ├── sources.py                  # ~80 feeds
│   ├── filters.py                  # Keyword + theme detection
│   ├── recurring_events.py         # Hardcoded annual summits
│   └── requirements.txt
├── data/
│   ├── publications.json           # PUBLIC feed
│   ├── publications-all.json       # Admin / audit
│   └── calendar.json               # Calendar feed
├── manual_events.yml               # YOU EDIT to add events
├── manual_excludes.yml             # YOU EDIT to suppress noise
└── README.md
```

---

Built for [Geschiedenis Actueel Think Tank](https://gathinktank.com).
