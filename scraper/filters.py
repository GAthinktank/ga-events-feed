"""
Keyword filtering and theme/region tagging.

The 'strict' filter is what the public WordPress page sees — it only passes
items that look like flagship publications, strategy papers, doctrines,
ministerial communiqués, or major announcements.

Multilingual: keyword lists cover EN, FR, DE, ES, IT, NL, PT.
"""
import re

# Strict-filter keywords — at least one must appear in title+summary
# to make it onto the public feed. Matched case-insensitively.
STRICT_KEYWORDS = [
    # English
    r"\bstrateg(y|ic|ies)\b", r"\bdoctrin(e|al)\b",
    r"\bwhite paper\b", r"\bgreen paper\b",
    r"\bnational security\b", r"\bdefen[cs]e review\b",
    r"\bintegrated review\b", r"\bsecurity strategy\b",
    r"\bforeign policy\b", r"\bposture review\b",
    r"\bcommuniqu[eé]\b", r"\bdeclaration\b",
    r"\bjoint statement\b", r"\bsummit\b",
    r"\baction plan\b", r"\broadmap\b",
    r"\bministerial\b", r"\bbilateral\b", r"\btrilateral\b",
    r"\bagreement\b", r"\baccord\b", r"\btreaty\b",
    r"\breport\b", r"\bannual\b", r"\byearbook\b",
    r"\bpolicy brief\b", r"\bworking paper\b",
    r"\bresearch paper\b", r"\bpolicy paper\b",
    r"\bnational interest\b",
    # French
    r"\bstrat[eé]gi(e|que)\b", r"\bdoctrine\b",
    r"\blivre blanc\b", r"\brevue strat[eé]gique\b",
    r"\bs[eé]curit[eé] nationale\b",
    r"\bd[eé]claration\b", r"\bsommet\b",
    r"\bcommuniqu[eé]\b", r"\baccord\b",
    r"\bnote d'analyse\b", r"\brapport\b",
    # German
    r"\bstrateg(ie|isch)\b", r"\bdoktrin\b",
    r"\bwei[ßs]buch\b", r"\bsicherheitsstrategie\b",
    r"\bnationale sicherheit\b", r"\bgipfel\b",
    r"\berkl[äa]rung\b", r"\babkommen\b",
    r"\barbeitspapier\b",
    # Spanish
    r"\bestrateg(ia|ico)\b", r"\bdoctrina\b",
    r"\blibro blanco\b", r"\bseguridad nacional\b",
    r"\bcumbre\b", r"\bdeclaraci[oó]n\b",
    r"\bcomunicado\b", r"\bacuerdo\b",
    # Italian
    r"\bstrateg(ia|ico)\b", r"\bdottrina\b",
    r"\blibro bianco\b", r"\bsicurezza nazionale\b",
    r"\bvertice\b", r"\bdichiarazione\b",
    r"\bcomunicato\b", r"\baccordo\b",
    # Dutch
    r"\bstrategi(e|sch)\b", r"\bdoctrine\b",
    r"\bwitboek\b", r"\bnationale veiligheid\b",
    r"\btop\b", r"\bverklaring\b",
    r"\bcommuniqu[eé]\b", r"\bovereenkomst\b",
    # Portuguese
    r"\bestrat[eé]gi(a|co)\b", r"\bdoutrina\b",
    r"\blivro branco\b", r"\bseguran[cç]a nacional\b",
    r"\bc[uú]pula\b", r"\bdeclara[cç][aã]o\b",
    r"\bcomunicado\b", r"\bacordo\b",
]

STRICT_RE = re.compile("|".join(STRICT_KEYWORDS), re.IGNORECASE)

# Soft block — exclude obvious noise even from the all-publications feed.
NOISE_KEYWORDS = [
    r"\binternship\b", r"\bjob (opening|vacancy)\b", r"\bcareer\b",
    r"\bfundraiser\b", r"\bgala\b", r"\balumni\b", r"\bnewsletter\b",
    r"\bpodcast\b",  # podcasts are not papers
    r"\bobituary\b", r"\bin memoriam\b",
]
NOISE_RE = re.compile("|".join(NOISE_KEYWORDS), re.IGNORECASE)

# Theme detection — from title+summary
THEMES = {
    "security": [
        r"\b(defen[cs]e|military|nato|nuclear|missile|deterren|posture|doctrine|war|conflict|terror)\b",
        r"\b(d[eé]fense|militaire|guerre|conflit)\b",
        r"\b(verteidigung|milit[äa]r|krieg|konflikt)\b",
        r"\b(defensa|militar|guerra|conflicto)\b",
        r"\b(difesa|militare|guerra|conflitto)\b",
        r"\b(defensie|militair|oorlog|conflict)\b",
        r"\b(defesa|guerra)\b",
    ],
    "diplomacy": [
        r"\b(diplomat|foreign affairs|bilateral|trilateral|summit|treaty|accord|ambassador|envoy)\b",
        r"\b(diplomati|sommet|trait[eé]|ambassad)\b",
        r"\b(diplomati|gipfel|botschaft)\b",
        r"\b(diplomac|cumbre|tratado|embajad)\b",
        r"\b(diplomaz|vertice|trattato|ambasciat)\b",
        r"\b(diplomati|top|verdrag|ambassad)\b",
        r"\b(diplomac|c[uú]pula|tratado|embaixad)\b",
    ],
    "economy": [
        r"\b(econom|trade|tariff|sanctions|gdp|monetary|fiscal|investment|wto|imf)\b",
        r"\b(commerce|tarif|sanction|investiss)\b",
        r"\b(handel|sanktion|investition)\b",
        r"\b(comercio|arancel|sanci[oó]n|inversi[oó]n)\b",
        r"\b(commerc|sanzion|investiment)\b",
        r"\b(handel|sanctie|investering)\b",
    ],
    "climate": [
        r"\b(climate|cop[0-9]+|emissions|carbon|net zero|biodiversity|unfccc)\b",
        r"\b(climat|émissions|carbone)\b",
        r"\b(klima|emission|kohlenstoff)\b",
        r"\b(clima|emisi[oó]n|carbono)\b",
        r"\b(clima|emissioni|carbonio)\b",
        r"\b(klimaat|emissie|koolstof)\b",
    ],
    "technology": [
        r"\b(ai|artificial intelligence|cyber|quantum|semiconductor|chip|tech sovereignty|digital)\b",
        r"\b(ia|intelligence artificielle|cyber|num[eé]rique)\b",
        r"\b(ki|cyber|digital)\b",
        r"\b(ia|inteligencia artificial|cibern|digital)\b",
        r"\b(ia|intelligenza artificiale|digitale)\b",
        r"\b(ai|cyber|digitaal)\b",
    ],
    "development": [
        r"\b(development aid|humanitarian|sdg|poverty|food security|refugee)\b",
        r"\b(d[eé]veloppement|humanitaire|pauvret[eé]|r[eé]fugi[eé])\b",
        r"\b(entwicklung|humanit[äa]r|armut|fl[üu]chtling)\b",
        r"\b(desarrollo|humanitari|pobreza|refugiad)\b",
        r"\b(sviluppo|umanitar|povert[aà]|rifugiat)\b",
        r"\b(ontwikkeling|humanitair|armoede|vluchteling)\b",
    ],
}
THEME_RES = {k: re.compile("|".join(v), re.IGNORECASE) for k, v in THEMES.items()}

# Region keywords for region detection from title+summary (overrides source default
# only if a strong signal is present)
REGION_HINTS = {
    "RU": [r"\b(russia|russian|moscow|kremlin|putin)\b", r"\b(russie|russe)\b", r"\b(russland|russisch)\b",
           r"\b(rusia|ruso)\b", r"\b(russia|russo)\b"],
    "CN": [r"\b(china|chinese|beijing|xi jinping|xi)\b", r"\b(chine|chinois)\b", r"\b(china|chinesisch)\b",
           r"\b(china|chino)\b", r"\b(cina|cinese)\b"],
    "IN": [r"\b(india|indian|new delhi|modi)\b", r"\b(inde|indien)\b", r"\b(indien|indisch)\b",
           r"\b(india|indio)\b", r"\b(india|indiano)\b"],
}
REGION_HINT_RES = {k: re.compile("|".join(v), re.IGNORECASE) for k, v in REGION_HINTS.items()}


def is_noise(text: str) -> bool:
    return bool(NOISE_RE.search(text or ""))


def is_strict(text: str) -> bool:
    """Does this item look like a flagship publication / strategic paper?"""
    return bool(STRICT_RE.search(text or ""))


def detect_theme(text: str):
    text = text or ""
    for theme, regex in THEME_RES.items():
        if regex.search(text):
            return theme
    return None


def detect_region_hint(text: str):
    text = text or ""
    for region, regex in REGION_HINT_RES.items():
        if regex.search(text):
            return region
    return None
