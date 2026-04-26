"""
GA! Events Feed — Source list (hybrid: direct RSS + Google News).

Sources are split into two groups:

  DIRECT_SOURCES — institutional RSS feeds that we know work directly.
                   These give us the cleanest, most authoritative items.

  GOOGLE_NEWS_SOURCES — wrapped Google News searches. These cover everything
                       else (NATO, UN, ministries that block scrapers, etc.).
                       Items come from news outlets reporting on the
                       institution, often including the institution's own
                       press releases at the top.

Both lists feed into the same scraper pipeline.
"""
from urllib.parse import quote

# Google News RSS endpoint format. We always use English-language Google News
# regardless of source language, because it has the broadest indexing. The
# `lang` field below is for UI tagging, not the search itself.
GNEWS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def gn(query):
    """Build a Google News RSS URL from a search query."""
    return GNEWS.format(q=quote(query))


# ============================================================
# DIRECT FEEDS — verified working from previous scrape runs
# ============================================================
DIRECT_SOURCES = [
    # ---- US ----
    {"name": "US Department of Defense", "type": "gov", "region": "US", "lang": "en",
     "url": "https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=945&max=20", "kind": "rss"},

    # ---- UK ----
    {"name": "UK FCDO", "type": "gov", "region": "UK", "lang": "en",
     "url": "https://www.gov.uk/government/organisations/foreign-commonwealth-development-office.atom", "kind": "atom"},
    {"name": "UK Ministry of Defence", "type": "gov", "region": "UK", "lang": "en",
     "url": "https://www.gov.uk/government/organisations/ministry-of-defence.atom", "kind": "atom"},

    # ---- EU institutions ----
    {"name": "European Commission — Press", "type": "gov", "region": "EU", "lang": "en",
     "url": "https://ec.europa.eu/commission/presscorner/api/rss?language=en", "kind": "rss"},
    {"name": "European Parliament — News", "type": "gov", "region": "EU", "lang": "en",
     "url": "https://www.europarl.europa.eu/rss/doc/top-stories/en.xml", "kind": "rss"},

    # ---- European countries ----
    {"name": "Norway — Government", "type": "gov", "region": "NO", "lang": "en",
     "url": "https://www.regjeringen.no/en/rss/Rss/2581615/", "kind": "rss"},
    {"name": "Belgium — Diplomatie", "type": "gov", "region": "BE", "lang": "fr",
     "url": "https://diplomatie.belgium.be/fr/rss.xml", "kind": "rss"},

    # ---- IOs ----
    {"name": "IMF", "type": "io", "region": "Global", "lang": "en",
     "url": "https://www.imf.org/en/News/RSS?Language=ENG", "kind": "rss"},
    {"name": "ASEAN", "type": "io", "region": "Asia", "lang": "en",
     "url": "https://asean.org/feed/", "kind": "rss"},

    # ---- US think tanks ----
    {"name": "Carnegie Endowment", "type": "tt", "region": "US", "lang": "en",
     "url": "https://carnegieendowment.org/rss/solr/?fa=publications&maxRows=20", "kind": "rss"},
    {"name": "Atlantic Council", "type": "tt", "region": "US", "lang": "en",
     "url": "https://www.atlanticcouncil.org/feed/", "kind": "rss"},
    {"name": "Hudson Institute", "type": "tt", "region": "US", "lang": "en",
     "url": "https://www.hudson.org/rss.xml", "kind": "rss"},
    {"name": "GMF — German Marshall Fund", "type": "tt", "region": "US", "lang": "en",
     "url": "https://www.gmfus.org/rss.xml", "kind": "rss"},
    {"name": "CEPA", "type": "tt", "region": "US", "lang": "en",
     "url": "https://cepa.org/feed/", "kind": "rss"},

    # ---- European think tanks ----
    {"name": "ECFR", "type": "tt", "region": "EU", "lang": "en",
     "url": "https://ecfr.eu/feed/", "kind": "rss"},
    {"name": "Egmont Institute (BE)", "type": "tt", "region": "EU", "lang": "en",
     "url": "https://www.egmontinstitute.be/feed/", "kind": "rss"},
    {"name": "HCSS (NL)", "type": "tt", "region": "NL", "lang": "en",
     "url": "https://hcss.nl/feed/", "kind": "rss"},
    {"name": "IFRI (FR)", "type": "tt", "region": "FR", "lang": "fr",
     "url": "https://www.ifri.org/fr/rss.xml", "kind": "rss"},
    {"name": "DGAP (DE)", "type": "tt", "region": "DE", "lang": "en",
     "url": "https://dgap.org/en/rss.xml", "kind": "rss"},
    {"name": "Real Instituto Elcano (ES)", "type": "tt", "region": "ES", "lang": "es",
     "url": "https://www.realinstitutoelcano.org/feed/", "kind": "rss"},
    {"name": "CIDOB (ES)", "type": "tt", "region": "ES", "lang": "es",
     "url": "https://www.cidob.org/en/rss.xml", "kind": "rss"},
    {"name": "IAI (IT)", "type": "tt", "region": "IT", "lang": "en",
     "url": "https://www.iai.it/en/rss.xml", "kind": "rss"},
    {"name": "FIIA (FI)", "type": "tt", "region": "FI", "lang": "en",
     "url": "https://www.fiia.fi/en/feed", "kind": "rss"},

    # ---- Asia-Pacific ----
    {"name": "ASPI (AU)", "type": "tt", "region": "AU", "lang": "en",
     "url": "https://www.aspi.org.au/feed", "kind": "rss"},
]


# ============================================================
# GOOGLE NEWS-BACKED SOURCES
# Each query targets either site:domain.tld or institution name.
# 'lang' field is for UI display; the search runs in en-US.
# ============================================================
GOOGLE_NEWS_SOURCES = [
    # ---- US Government ----
    {"name": "US State Department", "type": "gov", "region": "US", "lang": "en",
     "url": gn('site:state.gov (strategy OR statement OR briefing OR communique OR readout OR review)'), "kind": "rss"},
    {"name": "US White House", "type": "gov", "region": "US", "lang": "en",
     "url": gn('site:whitehouse.gov (statement OR fact-sheet OR readout OR strategy)'), "kind": "rss"},
    {"name": "US Congressional Research", "type": "gov", "region": "US", "lang": "en",
     "url": gn('site:crsreports.congress.gov OR "CRS report"'), "kind": "rss"},

    # ---- UK ----
    {"name": "UK gov.uk announcements", "type": "gov", "region": "UK", "lang": "en",
     "url": gn('site:gov.uk (foreign OR defence OR strategy OR review OR communique)'), "kind": "rss"},

    # ---- EU institutions ----
    {"name": "European External Action Service", "type": "gov", "region": "EU", "lang": "en",
     "url": gn('"EEAS" OR "European External Action Service" (statement OR communique OR strategy)'), "kind": "rss"},
    {"name": "European Council", "type": "gov", "region": "EU", "lang": "en",
     "url": gn('site:consilium.europa.eu (conclusions OR statement OR meeting)'), "kind": "rss"},

    # ---- European individual countries ----
    {"name": "France — MEAE (Diplomatie)", "type": "gov", "region": "FR", "lang": "fr",
     "url": gn('site:diplomatie.gouv.fr OR ("Ministere Europe Affaires etrangeres" declaration)'), "kind": "rss"},
    {"name": "France — Ministère des Armées", "type": "gov", "region": "FR", "lang": "fr",
     "url": gn('site:defense.gouv.fr OR "Ministere des Armees" strategie'), "kind": "rss"},
    {"name": "Germany — Auswärtiges Amt", "type": "gov", "region": "DE", "lang": "de",
     "url": gn('site:auswaertiges-amt.de OR "Auswartiges Amt" (Strategie OR Erklarung)'), "kind": "rss"},
    {"name": "Germany — Bundesregierung", "type": "gov", "region": "DE", "lang": "de",
     "url": gn('site:bundesregierung.de (Sicherheit OR Aussenpolitik OR Strategie)'), "kind": "rss"},
    {"name": "Netherlands — Buitenlandse Zaken", "type": "gov", "region": "NL", "lang": "nl",
     "url": gn('site:rijksoverheid.nl "Buitenlandse Zaken" (verklaring OR strategie OR beleid)'), "kind": "rss"},
    {"name": "Netherlands — Defensie", "type": "gov", "region": "NL", "lang": "nl",
     "url": gn('site:defensie.nl OR site:rijksoverheid.nl "Ministerie van Defensie"'), "kind": "rss"},
    {"name": "Spain — MAEC", "type": "gov", "region": "ES", "lang": "es",
     "url": gn('site:exteriores.gob.es OR "Ministerio de Asuntos Exteriores" Espana'), "kind": "rss"},
    {"name": "Italy — Esteri", "type": "gov", "region": "IT", "lang": "it",
     "url": gn('site:esteri.it (dichiarazione OR strategia OR vertice)'), "kind": "rss"},
    {"name": "Poland — MFA", "type": "gov", "region": "PL", "lang": "en",
     "url": gn('"Polish Foreign Ministry" OR site:gov.pl/web/diplomacy'), "kind": "rss"},
    {"name": "Sweden — Government", "type": "gov", "region": "SE", "lang": "en",
     "url": gn('site:government.se (foreign OR defence OR strategy)'), "kind": "rss"},
    {"name": "Finland — Government", "type": "gov", "region": "FI", "lang": "en",
     "url": gn('site:valtioneuvosto.fi/en (foreign OR defence)'), "kind": "rss"},
    {"name": "Denmark — MFA", "type": "gov", "region": "DK", "lang": "en",
     "url": gn('site:um.dk OR "Danish Ministry of Foreign Affairs"'), "kind": "rss"},
    {"name": "Ireland — DFA", "type": "gov", "region": "IE", "lang": "en",
     "url": gn('site:dfa.ie OR "Irish Department of Foreign Affairs"'), "kind": "rss"},
    {"name": "Austria — BMEIA", "type": "gov", "region": "AT", "lang": "de",
     "url": gn('site:bmeia.gv.at OR "Aussenministerium" Osterreich'), "kind": "rss"},

    # ---- International Organizations ----
    {"name": "NATO", "type": "io", "region": "Global", "lang": "en",
     "url": gn('site:nato.int OR ("NATO" (summit OR communique OR statement OR declaration OR strategy))'), "kind": "rss"},
    {"name": "United Nations", "type": "io", "region": "Global", "lang": "en",
     "url": gn('site:un.org (statement OR resolution OR Security Council OR Secretary-General)'), "kind": "rss"},
    {"name": "UN Security Council", "type": "io", "region": "Global", "lang": "en",
     "url": gn('"UN Security Council" (resolution OR statement OR meeting)'), "kind": "rss"},
    {"name": "World Bank", "type": "io", "region": "Global", "lang": "en",
     "url": gn('site:worldbank.org (report OR strategy OR statement)'), "kind": "rss"},
    {"name": "OECD", "type": "io", "region": "Global", "lang": "en",
     "url": gn('site:oecd.org (report OR communique OR ministerial)'), "kind": "rss"},
    {"name": "OSCE", "type": "io", "region": "EU", "lang": "en",
     "url": gn('site:osce.org OR "OSCE" (statement OR meeting OR mission)'), "kind": "rss"},
    {"name": "WTO", "type": "io", "region": "Global", "lang": "en",
     "url": gn('site:wto.org (ministerial OR communique OR dispute OR decision)'), "kind": "rss"},
    {"name": "Council of Europe", "type": "io", "region": "EU", "lang": "en",
     "url": gn('site:coe.int OR "Council of Europe" (declaration OR resolution)'), "kind": "rss"},
    {"name": "African Union", "type": "io", "region": "Africa", "lang": "en",
     "url": gn('"African Union" (summit OR communique OR statement OR declaration)'), "kind": "rss"},
    {"name": "OAS — Organization of American States", "type": "io", "region": "LatAm", "lang": "en",
     "url": gn('"Organization of American States" OR "OEA" (resolution OR declaration)'), "kind": "rss"},

    # ---- US think tanks ----
    {"name": "Brookings", "type": "tt", "region": "US", "lang": "en",
     "url": gn('site:brookings.edu (report OR analysis OR policy OR brief)'), "kind": "rss"},
    {"name": "Council on Foreign Relations", "type": "tt", "region": "US", "lang": "en",
     "url": gn('site:cfr.org (report OR analysis OR brief)'), "kind": "rss"},
    {"name": "CSIS", "type": "tt", "region": "US", "lang": "en",
     "url": gn('site:csis.org (report OR analysis OR brief)'), "kind": "rss"},
    {"name": "RAND", "type": "tt", "region": "US", "lang": "en",
     "url": gn('site:rand.org (report OR research)'), "kind": "rss"},
    {"name": "Wilson Center", "type": "tt", "region": "US", "lang": "en",
     "url": gn('site:wilsoncenter.org (report OR analysis)'), "kind": "rss"},
    {"name": "PIIE — Peterson Institute", "type": "tt", "region": "US", "lang": "en",
     "url": gn('site:piie.com (working paper OR policy brief OR analysis)'), "kind": "rss"},

    # ---- UK / European think tanks ----
    {"name": "Chatham House", "type": "tt", "region": "UK", "lang": "en",
     "url": gn('site:chathamhouse.org (report OR research OR briefing)'), "kind": "rss"},
    {"name": "IISS", "type": "tt", "region": "UK", "lang": "en",
     "url": gn('site:iiss.org (report OR analysis OR Military Balance OR Strategic Survey)'), "kind": "rss"},
    {"name": "RUSI", "type": "tt", "region": "UK", "lang": "en",
     "url": gn('site:rusi.org (report OR analysis OR commentary)'), "kind": "rss"},
    {"name": "Bruegel", "type": "tt", "region": "EU", "lang": "en",
     "url": gn('site:bruegel.org (policy brief OR working paper OR analysis)'), "kind": "rss"},
    {"name": "CEPS", "type": "tt", "region": "EU", "lang": "en",
     "url": gn('site:ceps.eu (policy brief OR working paper OR report)'), "kind": "rss"},
    {"name": "Centre for European Reform (CER)", "type": "tt", "region": "UK", "lang": "en",
     "url": gn('site:cer.eu (report OR brief OR insight)'), "kind": "rss"},
    {"name": "European Policy Centre (EPC)", "type": "tt", "region": "EU", "lang": "en",
     "url": gn('site:epc.eu (commentary OR analysis OR report)'), "kind": "rss"},
    {"name": "Clingendael (NL)", "type": "tt", "region": "NL", "lang": "en",
     "url": gn('site:clingendael.org (report OR policy brief OR commentary)'), "kind": "rss"},
    {"name": "FRS — Recherche Stratégique (FR)", "type": "tt", "region": "FR", "lang": "fr",
     "url": gn('site:frstrategie.org OR "Fondation pour la Recherche Strategique"'), "kind": "rss"},
    {"name": "SWP Berlin (DE)", "type": "tt", "region": "DE", "lang": "en",
     "url": gn('site:swp-berlin.org (analysis OR comment OR research paper)'), "kind": "rss"},
    {"name": "PISM (PL)", "type": "tt", "region": "PL", "lang": "en",
     "url": gn('site:pism.pl (analysis OR brief OR strategic file)'), "kind": "rss"},
    {"name": "GLOBSEC", "type": "tt", "region": "EU", "lang": "en",
     "url": gn('site:globsec.org (report OR brief OR analysis)'), "kind": "rss"},
    {"name": "SIPRI", "type": "tt", "region": "EU", "lang": "en",
     "url": gn('site:sipri.org OR "SIPRI" (yearbook OR report OR analysis)'), "kind": "rss"},
    {"name": "DIIS (DK)", "type": "tt", "region": "DK", "lang": "en",
     "url": gn('site:diis.dk (report OR analysis OR brief)'), "kind": "rss"},
    {"name": "NUPI (NO)", "type": "tt", "region": "NO", "lang": "en",
     "url": gn('site:nupi.no (report OR analysis OR brief)'), "kind": "rss"},
    {"name": "International Crisis Group", "type": "tt", "region": "Global", "lang": "en",
     "url": gn('site:crisisgroup.org (report OR briefing OR statement)'), "kind": "rss"},
    {"name": "MERICS — China analysis", "type": "tt", "region": "DE", "lang": "en",
     "url": gn('site:merics.org OR "MERICS" (report OR analysis)'), "kind": "rss"},

    # ---- Russia ----
    {"name": "Russia — MFA", "type": "gov", "region": "RU", "lang": "en",
     "url": gn('"Russian Foreign Ministry" OR "Lavrov" (statement OR press OR briefing)'), "kind": "rss"},
    {"name": "Valdai Club", "type": "tt", "region": "RU", "lang": "en",
     "url": gn('site:valdaiclub.com OR "Valdai Discussion Club"'), "kind": "rss"},
    {"name": "RIAC — Russian Int. Affairs Council", "type": "tt", "region": "RU", "lang": "en",
     "url": gn('site:russiancouncil.ru OR "Russian International Affairs Council"'), "kind": "rss"},

    # ---- India ----
    {"name": "India — MEA", "type": "gov", "region": "IN", "lang": "en",
     "url": gn('site:mea.gov.in OR "Indian Ministry of External Affairs"'), "kind": "rss"},
    {"name": "ORF — Observer Research Foundation", "type": "tt", "region": "IN", "lang": "en",
     "url": gn('site:orfonline.org (report OR analysis OR brief)'), "kind": "rss"},
    {"name": "IDSA — Manohar Parrikar Institute", "type": "tt", "region": "IN", "lang": "en",
     "url": gn('site:idsa.in OR "Manohar Parrikar Institute"'), "kind": "rss"},

    # ---- China analysis ----
    {"name": "China — MFA", "type": "gov", "region": "CN", "lang": "en",
     "url": gn('"Chinese Foreign Ministry" (briefing OR statement OR press conference)'), "kind": "rss"},
    {"name": "Carnegie China", "type": "tt", "region": "CN", "lang": "en",
     "url": gn('"Carnegie China" OR "carnegieendowment.org/china"'), "kind": "rss"},

    # ---- Asia-Pacific ----
    {"name": "Japan — MOFA", "type": "gov", "region": "JP", "lang": "en",
     "url": gn('site:mofa.go.jp (statement OR press OR communique)'), "kind": "rss"},
    {"name": "South Korea — MOFA", "type": "gov", "region": "KR", "lang": "en",
     "url": gn('"South Korean Foreign Ministry" OR "Korea MOFA"'), "kind": "rss"},
    {"name": "Australia — DFAT", "type": "gov", "region": "AU", "lang": "en",
     "url": gn('site:dfat.gov.au (statement OR strategy)'), "kind": "rss"},
    {"name": "Lowy Institute (AU)", "type": "tt", "region": "AU", "lang": "en",
     "url": gn('site:lowyinstitute.org (analysis OR report)'), "kind": "rss"},
    {"name": "RSIS Singapore", "type": "tt", "region": "Asia", "lang": "en",
     "url": gn('site:rsis.edu.sg (commentary OR working paper OR policy report)'), "kind": "rss"},

    # ---- Africa ----
    {"name": "ISS Africa", "type": "tt", "region": "Africa", "lang": "en",
     "url": gn('site:issafrica.org (report OR analysis OR ISS today)'), "kind": "rss"},
    {"name": "South Africa — DIRCO", "type": "gov", "region": "Africa", "lang": "en",
     "url": gn('site:dirco.gov.za OR "South African Department of International Relations"'), "kind": "rss"},
    {"name": "Nigeria — MFA", "type": "gov", "region": "Africa", "lang": "en",
     "url": gn('"Nigerian Ministry of Foreign Affairs" OR site:foreignaffairs.gov.ng'), "kind": "rss"},
    {"name": "Kenya — MFA", "type": "gov", "region": "Africa", "lang": "en",
     "url": gn('"Kenya Ministry of Foreign Affairs" OR site:mfa.go.ke'), "kind": "rss"},

    # ---- Latin America ----
    {"name": "Brazil — Itamaraty", "type": "gov", "region": "LatAm", "lang": "pt",
     "url": gn('site:gov.br/mre OR "Itamaraty" (declaracao OR comunicado)'), "kind": "rss"},
    {"name": "Mexico — SRE", "type": "gov", "region": "LatAm", "lang": "es",
     "url": gn('site:gob.mx/sre OR "Secretaria de Relaciones Exteriores"'), "kind": "rss"},
    {"name": "Argentina — Cancillería", "type": "gov", "region": "LatAm", "lang": "es",
     "url": gn('site:cancilleria.gob.ar OR "Cancilleria argentina"'), "kind": "rss"},
    {"name": "Chile — Cancillería", "type": "gov", "region": "LatAm", "lang": "es",
     "url": gn('site:minrel.gob.cl OR "Cancilleria de Chile"'), "kind": "rss"},
    {"name": "CARI Argentina", "type": "tt", "region": "LatAm", "lang": "es",
     "url": gn('site:cari.com.ar OR "Consejo Argentino para las Relaciones Internacionales"'), "kind": "rss"},
]


# Combined master list (this is what main.py imports)
SOURCES = DIRECT_SOURCES + GOOGLE_NEWS_SOURCES
