from datetime import date
from io import BytesIO
from pathlib import Path
import re
from urllib.parse import quote_plus, unquote, urlparse

import pandas as pd
import gspread
import requests
import streamlit as st
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
from pypdf import PdfReader
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


SALARY_FLOOR = 200_000
ICLOUD_STORAGE_DIR = Path(
    "/Users/Selina/Library/Mobile Documents/com~apple~CloudDocs/Selina Opportunity Dashboard"
)


st.set_page_config(
    page_title="Selina Opportunity Dashboard",
    page_icon="💼",
    layout="wide",
)


BACKGROUND_SIGNALS = [
    "Former Cboe economist, data scientist, and quantitative researcher",
    "Economist background",
    "Market structure expertise",
    "Brokerage, exchange, and trading ecosystem expertise",
    "Public speaking and executive communication",
    "Research publications",
    "Quantitative research education",
    "Mandarin language advantage when relevant",
]

TARGET_COMPANIES = {
    "Brokerage / retail investing": [
        "Fidelity",
        "Charles Schwab",
        "Interactive Brokers",
        "Robinhood",
        "Clear Street",
    ],
    "Exchanges / market infrastructure": [
        "Cboe",
        "CME Group",
        "Nasdaq",
        "NYSE / ICE",
        "IEX",
    ],
    "Prediction markets / event contracts": [
        "Kalshi",
        "Polymarket",
        "DraftKings",
        "Crypto.com / event markets",
    ],
    "Research, asset management, trust, and banking": [
        "Morningstar",
        "Northern Trust",
        "Wells Fargo",
        "BlackRock",
        "State Street",
        "Fitch",
        "William Blair",
        "Northwestern Mutual",
    ],
    "Consulting and advisory": [
        "KPMG",
        "Deloitte",
        "EY",
        "PwC",
        "McKinsey",
        "BCG",
    ],
    "Digital assets / FinTech": [
        "Coinbase",
        "Anchorage Digital",
        "Affirm",
        "SoFi",
        "Stripe",
        "Block",
    ],
}

SEARCH_QUERIES = [
    "market structure director Chicago remote",
    "brokerage strategy market structure options",
    "quantitative researcher market microstructure",
    "research director financial markets Chicago",
    "product strategy brokerage trading",
    "event contracts prediction markets strategy",
    "financial services data science director Chicago",
]

SOURCE_LINKS = {
    "LinkedIn Saved Jobs": "https://www.linkedin.com/jobs/saved/",
    "LinkedIn Job Alerts": "https://www.linkedin.com/jobs/alerts/",
    "Indeed": "https://www.indeed.com/jobs?q=market+structure+director+finance&l=Chicago%2C+IL",
    "Google Jobs Search": "https://www.google.com/search?q=market+structure+director+finance+Chicago+remote+jobs",
}

CAREER_PAGES = {
    "Morningstar": "https://www.morningstar.com/company/careers",
    "CME Group": "https://www.cmegroup.com/careers.html",
    "Nasdaq": "https://www.nasdaq.com/about/careers",
    "Fitch": "https://www.fitch.group/careers",
    "Akuna Capital": "https://akunacapital.com/careers",
    "Clear Street": "https://clearstreet.io/careers/",
    "William Blair": "https://www.williamblair.com/Careers",
    "Northwestern Mutual": "https://www.northwesternmutual.com/careers/",
    "Cboe": "https://www.cboe.com/about/careers/",
    "ICE": "https://www.ice.com/careers",
    "Robinhood": "https://careers.robinhood.com/",
    "Coinbase": "https://www.coinbase.com/careers",
    "Anchorage Digital": "https://www.anchorage.com/careers",
    "Affirm": "https://www.affirm.com/careers",
}

APPLICATION_COLUMNS = [
    "saved_at",
    "company",
    "role",
    "status",
    "applied_date",
    "follow_up_date",
    "fit_score",
    "link",
    "notes",
]

OUTREACH_COLUMNS = [
    "saved_at",
    "contact_name",
    "company",
    "contact_role",
    "relationship",
    "status",
    "message_date",
    "follow_up_date",
    "related_job",
    "notes",
]

JOB_COLUMNS = [
    "id",
    "title",
    "company",
    "location",
    "salary",
    "tier",
    "fit_score",
    "link",
    "source_notes",
    "strengths",
    "gaps",
    "why",
    "keywords",
]


def ensure_icloud_storage():
    ICLOUD_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return ICLOUD_STORAGE_DIR


def csv_path(filename):
    return ensure_icloud_storage() / filename


def load_csv_records(filename, columns):
    path = csv_path(filename)
    if not path.exists():
        return []
    try:
        return pd.read_csv(path).fillna("").to_dict("records")
    except Exception:
        return []


def append_csv_row(filename, columns, row):
    path = csv_path(filename)
    safe_row = {column: str(row.get(column, "")) for column in columns}
    frame = pd.DataFrame([safe_row], columns=columns)
    frame.to_csv(path, mode="a", index=False, header=not path.exists())
    return path


def split_cell(value):
    if not value:
        return []
    return [item.strip() for item in str(value).split(" | ") if item.strip()]


def serialize_job(job):
    return {
        "id": job["id"],
        "title": job["title"],
        "company": job["company"],
        "location": job["location"],
        "salary": job["salary"],
        "tier": job["tier"],
        "fit_score": job["fit_score"],
        "link": job["link"],
        "source_notes": job.get("source_notes", ""),
        "strengths": " | ".join(job.get("strengths", [])),
        "gaps": " | ".join(job.get("gaps", [])),
        "why": job.get("why", ""),
        "keywords": " | ".join(job.get("keywords", [])),
    }


def deserialize_job(row):
    return {
        "id": int(row.get("id", 0) or 0),
        "title": row.get("title", "Untitled Role"),
        "company": row.get("company", "Company TBD"),
        "location": row.get("location", "Location TBD"),
        "salary": row.get("salary", "Salary not posted"),
        "tier": row.get("tier", "Unclassified: Needs review"),
        "fit_score": int(float(row.get("fit_score", 0) or 0)),
        "link": row.get("link", "https://www.linkedin.com/jobs/"),
        "source_notes": row.get("source_notes", ""),
        "strengths": split_cell(row.get("strengths", "")),
        "gaps": split_cell(row.get("gaps", "")),
        "why": row.get("why", ""),
        "keywords": split_cell(row.get("keywords", "")),
    }


def google_sheets_configured():
    try:
        return "gcp_service_account" in st.secrets and "google_sheet_id" in st.secrets
    except Exception:
        return False


@st.cache_resource
def get_google_sheet():
    if not google_sheets_configured():
        return None
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes,
    )
    client = gspread.authorize(credentials)
    return client.open_by_key(st.secrets["google_sheet_id"])


def get_or_create_worksheet(sheet, title, columns):
    try:
        worksheet = sheet.worksheet(title)
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=title, rows=500, cols=len(columns))
        worksheet.append_row(columns)
        return worksheet

    existing_values = worksheet.get_all_values()
    if not existing_values:
        worksheet.append_row(columns)
    return worksheet


def append_sheet_row(tab_name, columns, row):
    sheet = get_google_sheet()
    if sheet is None:
        return False, "Google Sheets is not configured yet."
    try:
        worksheet = get_or_create_worksheet(sheet, tab_name, columns)
        worksheet.append_row([str(row.get(column, "")) for column in columns])
        return True, f"Saved to Google Sheet tab: {tab_name}."
    except Exception as exc:
        return False, f"Could not save to Google Sheets: {exc}"


def load_sheet_records(tab_name, columns):
    sheet = get_google_sheet()
    if sheet is None:
        return []
    try:
        worksheet = get_or_create_worksheet(sheet, tab_name, columns)
        return worksheet.get_all_records()
    except Exception:
        return []


def extract_salary_numbers(text):
    clean_text = text.lower().replace(",", "")
    numbers = []
    for match in re.finditer(r"\$?\s*(\d{2,3})(?:\s*k|\s*000)?", clean_text):
        value = int(match.group(1))
        if value < 50:
            continue
        if value < 1000:
            value *= 1000
        numbers.append(value)
    return numbers


def evaluate_salary_fit(salary_text):
    salary_numbers = extract_salary_numbers(salary_text)
    if not salary_numbers:
        return 0, None

    max_salary = max(salary_numbers)
    min_salary = min(salary_numbers)
    if max_salary < SALARY_FLOOR:
        return -14, f"Posted compensation appears below Selina's $200K+ market target; visible range tops out near ${max_salary:,}."
    if min_salary >= SALARY_FLOOR:
        return 8, "Posted compensation appears to meet Selina's $200K+ market target."
    return 3, "Compensation range may reach Selina's $200K+ target, but the lower end is below target."


def title_from_url(link):
    if not link:
        return ""
    path_parts = [part for part in urlparse(link).path.split("/") if part]
    if not path_parts:
        return ""
    slug = unquote(path_parts[-1]).split("?")[0]
    slug = re.sub(r"[-_]+", " ", slug)
    slug = re.sub(r"\s+", " ", slug).strip()
    if not slug or slug.lower() in {"job", "jobs", "careers"}:
        return ""
    return slug.title()


def infer_company_from_link(link):
    hostname = urlparse(link).netloc.lower()
    domain_map = {
        "morningstar": "Morningstar",
        "cmegroup": "CME Group",
        "nasdaq": "Nasdaq",
        "fitch": "Fitch",
        "akunacapital": "Akuna Capital",
        "clearstreet": "Clear Street",
        "williamblair": "William Blair",
        "northwesternmutual": "Northwestern Mutual",
        "cboe": "Cboe",
        "ice": "ICE",
        "robinhood": "Robinhood",
        "coinbase": "Coinbase",
        "anchorage": "Anchorage Digital",
        "affirm": "Affirm",
        "schwab": "Charles Schwab",
        "fidelity": "Fidelity",
        "interactivebrokers": "Interactive Brokers",
    }
    for domain_hint, company_name in domain_map.items():
        if domain_hint in hostname:
            return company_name
    return ""


def clean_page_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(Apply now|Share|Save job|Back to search)", " ", text, flags=re.I)
    return text.strip()


def fetch_job_page(link):
    if not link:
        return "", "No link entered."
    try:
        response = requests.get(
            link,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0 Safari/537.36"
                )
            },
            timeout=12,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return "", f"Could not fetch the page automatically: {exc}"

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        tag.decompose()

    title_parts = []
    if soup.title and soup.title.string:
        title_parts.append(soup.title.string)
    for selector in [
        "h1",
        '[class*="job-title"]',
        '[class*="JobTitle"]',
        '[data-testid*="job"]',
    ]:
        found = soup.select_one(selector)
        if found:
            title_parts.append(found.get_text(" ", strip=True))

    page_text = clean_page_text(" ".join(title_parts + [soup.get_text(" ", strip=True)]))
    if len(page_text) < 200:
        return page_text, "Fetched the page, but it had very little readable text. The site may load content with JavaScript."
    return page_text[:12000], "Fetched job page successfully."


def extract_salary_text(page_text):
    salary_patterns = [
        r"\$\s?\d{2,3}(?:,\d{3})?\s?(?:k|K)?\s?[-–]\s?\$?\s?\d{2,3}(?:,\d{3})?\s?(?:k|K)?",
        r"\$\s?\d{2,3}(?:,\d{3})?\s?(?:k|K)?\+?",
        r"\d{2,3}\s?(?:k|K)\s?[-–]\s?\d{2,3}\s?(?:k|K)",
    ]
    for pattern in salary_patterns:
        match = re.search(pattern, page_text)
        if match:
            return match.group(0)
    return ""


def extract_location_text(page_text):
    location_terms = [
        "Chicago",
        "Remote",
        "New York",
        "Boston",
        "Dallas",
        "San Francisco",
        "Hybrid",
        "United States",
    ]
    found = [term for term in location_terms if re.search(rf"\b{re.escape(term)}\b", page_text, re.I)]
    return ", ".join(found[:3])


def extract_requirements_text(page_text):
    requirement_markers = [
        "requirements",
        "qualifications",
        "what you need",
        "what we're looking for",
        "responsibilities",
        "you will",
    ]
    lower_text = page_text.lower()
    starts = [lower_text.find(marker) for marker in requirement_markers if lower_text.find(marker) != -1]
    if not starts:
        return page_text[:1800]
    start = min(starts)
    return page_text[start : start + 2500]


def extract_job_details_from_page(link, page_text):
    inferred_title = title_from_url(link)
    inferred_company = infer_company_from_link(link)
    salary = extract_salary_text(page_text)
    location = extract_location_text(page_text)
    requirements = extract_requirements_text(page_text)

    h1_like_title = ""
    title_match = re.search(
        r"((?:Head|Director|Senior|Lead|Principal|Manager|VP|Vice President|Research)[A-Za-z0-9 ,/&+-]{10,90})",
        page_text,
    )
    if title_match:
        h1_like_title = title_match.group(1).strip()

    return {
        "title": h1_like_title or inferred_title,
        "company": inferred_company,
        "location": location,
        "salary": salary,
        "requirements": requirements,
    }


JOBS = [
    {
        "id": 1,
        "title": "Senior Manager / Director, Market Structure Strategy",
        "company": "Charles Schwab / Fidelity / Interactive Brokers target",
        "location": "Chicago, remote, or major U.S. finance hub",
        "salary": "$200K+ target",
        "tier": "Tier 1: Market Structure / Brokerage Strategy / Product Strategy",
        "fit_score": 94,
        "link": "https://www.schwabjobs.com/",
        "strengths": [
            "Directly aligned with Selina's Cboe market structure, economist, data science, and quantitative research background.",
            "Brokerage firms value expertise in trading behavior, options markets, market quality, routing, and investor analytics.",
            "Strong fit for public speaking, research publications, and executive-facing market narratives.",
        ],
        "gaps": [
            "May require product ownership, brokerage operations, or direct client-segment strategy experience.",
            "Application should translate Cboe market expertise into brokerage growth, product, and client insights.",
        ],
        "why": "This is the strongest lane: brokerage firms are close to Cboe's ecosystem and can pay well for market structure plus quantitative strategy.",
        "keywords": [
            "market structure",
            "brokerage strategy",
            "options markets",
            "order routing",
            "investor analytics",
            "product strategy",
            "quantitative research",
        ],
    },
    {
        "id": 2,
        "title": "Director, Exchange Strategy / Market Intelligence",
        "company": "IEX / Nasdaq / CME Group / ICE target",
        "location": "Chicago, New York, or remote-flexible",
        "salary": "$200K+ target",
        "tier": "Tier 1: Exchange Strategy / Market Intelligence / Research Director",
        "fit_score": 93,
        "link": "https://www.iex.io/careers/",
        "strengths": [
            "Very close to Selina's prior Cboe exchange, market structure, and market intelligence background.",
            "Strong match for research publications, public speaking, and competitive market analysis.",
            "Useful for roles involving market quality, exchange strategy, listings, products, and regulatory context.",
        ],
        "gaps": [
            "Some roles may prefer direct exchange product management or regulatory policy ownership.",
            "Need to avoid looking too Cboe-specific by showing broader market infrastructure perspective.",
        ],
        "why": "This keeps Selina closest to her strongest credibility: exchanges, market structure, research, and senior market communication.",
        "keywords": [
            "exchange strategy",
            "market quality",
            "market intelligence",
            "options",
            "equities",
            "market microstructure",
            "regulatory analysis",
        ],
    },
    {
        "id": 3,
        "title": "Research Director / Market Intelligence Lead",
        "company": "Morningstar / Northern Trust / BlackRock target",
        "location": "Chicago preferred, remote possible",
        "salary": "$200K+ target",
        "tier": "Tier 1: Research Director / Market Intelligence / Investment Strategy",
        "fit_score": 90,
        "link": "https://www.morningstar.com/company/careers",
        "strengths": [
            "Strong fit for economist background, research publications, market commentary, and investment analytics.",
            "Morningstar and Northern Trust are especially relevant because of Chicago presence and research-driven businesses.",
            "BlackRock may value market structure expertise for investment strategy, ETF, or market insights roles.",
        ],
        "gaps": [
            "May require direct portfolio construction, manager research, or wealth/advisor experience.",
            "Application should position Selina as a market/investment research leader rather than a pure academic economist.",
        ],
        "why": "These firms convert research and market expertise into client-facing investment strategy, which fits Selina's communication strengths.",
        "keywords": [
            "market intelligence",
            "investment research",
            "ETF strategy",
            "wealth strategy",
            "advisor insights",
            "economic research",
            "portfolio analytics",
        ],
    },
    {
        "id": 4,
        "title": "Strategy / Research Lead, Event Contracts and Prediction Markets",
        "company": "Kalshi / Polymarket / DraftKings target",
        "location": "Remote, New York, or Chicago-flexible",
        "salary": "$200K+ target",
        "tier": "Tier 2: AI/Quant/FinTech Product plus Event Market Strategy",
        "fit_score": 88,
        "link": "https://kalshi.com/careers",
        "strengths": [
            "Prediction and event markets connect directly to market design, contracts, trading behavior, and economic analysis.",
            "Cboe experience is a strong credibility signal for regulated markets and product-market structure.",
            "Quantitative research and public communication can support product strategy, market education, and policy narratives.",
        ],
        "gaps": [
            "May require startup tolerance, crypto/web3 context, sports betting context, or direct event-contract product experience.",
            "Some roles may be less stable than brokerage or asset management, so compensation and risk should be checked carefully.",
        ],
        "why": "This is a high-upside lane where Selina's market design background can be unusually differentiated.",
        "keywords": [
            "event contracts",
            "prediction markets",
            "market design",
            "fintech product",
            "trading behavior",
            "regulatory strategy",
        ],
    },
    {
        "id": 5,
        "title": "Capital Markets / Market Structure Advisory Director",
        "company": "Deloitte / KPMG / EY / PwC target",
        "location": "Chicago preferred, remote or travel-based",
        "salary": "$200K+ target",
        "tier": "Tier 1: Market Intelligence / Product Strategy / Financial Services Consulting",
        "fit_score": 85,
        "link": "https://www2.deloitte.com/us/en/careers/careers.html",
        "strengths": [
            "Consulting can monetize Selina's market structure, research, data science, and executive presentation strengths.",
            "Good path for financial services strategy, brokerage/exchange advisory, market intelligence, and analytics transformation.",
            "Public speaking and research publications are useful for client-facing credibility.",
        ],
        "gaps": [
            "May require consulting business development, client delivery, or heavy travel.",
            "Application should show practical business impact, not only research quality.",
        ],
        "why": "This is a paycheck-first lane with many openings, but the best targets should stay close to financial markets and analytics.",
        "keywords": [
            "financial services consulting",
            "market structure",
            "capital markets advisory",
            "data science",
            "analytics strategy",
            "client presentations",
        ],
    },
]


def evaluate_custom_job(title, company, location, salary, job_description):
    text = " ".join([title, company, location, salary, job_description]).lower()
    score = 58
    strengths = []
    gaps = []
    keywords = []

    tier_1_terms = [
        "investment strategist",
        "research director",
        "market intelligence",
        "product strategy",
        "financial analytics",
        "commercial finance",
        "capital markets",
        "market structure",
        "exchange",
        "brokerage",
        "broker-dealer",
        "options",
        "order routing",
        "market quality",
    ]
    tier_2_terms = [
        "ai",
        "artificial intelligence",
        "quantitative research",
        "quant",
        "fintech",
        "machine learning",
        "prediction market",
        "event contract",
        "market design",
    ]
    tier_3_terms = [
        "wealth",
        "family office",
        "mandarin",
        "chinese",
        "private wealth",
    ]
    priority_companies = [
        "fidelity",
        "charles schwab",
        "schwab",
        "interactive brokers",
        "cboe",
        "cme",
        "nasdaq",
        "nyse",
        "ice",
        "iex",
        "kalshi",
        "polymarket",
        "draftkings",
        "morningstar",
        "northern trust",
        "wells fargo",
        "blackrock",
        "fitch",
        "akuna",
        "akuna capital",
        "clear street",
        "william blair",
        "northwestern",
        "northwestern mutual",
        "coinbase",
        "anchorage",
        "anchorage digital",
        "affirm",
        "kpmg",
        "deloitte",
        "ey",
        "pwc",
    ]

    if any(company_name in text for company_name in priority_companies):
        score += 10
        strengths.append("Company is on Selina's priority target list.")

    if any(term in text for term in tier_1_terms):
        score += 17
        tier = "Tier 1: Investment Strategy / Market Intelligence / Product Strategy / Financial Analytics"
        strengths.append("Strong match to Selina's highest-priority strategy, research, or financial analytics targets.")
    elif any(term in text for term in tier_2_terms):
        score += 14
        tier = "Tier 2: AI in Finance / Quantitative Research / FinTech Product"
        strengths.append("Good match to AI-in-finance, quantitative research, or FinTech interests.")
    elif any(term in text for term in tier_3_terms):
        score += 12
        tier = "Tier 3: Wealth Strategy / Family Office / Mandarin-relevant"
        strengths.append("Relevant to wealth strategy, family office research, or Mandarin language advantage.")
    else:
        tier = "Unclassified: Needs review"
        gaps.append("Role does not clearly match the three target tiers from the information entered.")

    if "chicago" in text:
        score += 8
        strengths.append("Chicago location is strongly aligned with Selina's preference.")
    elif "remote" in text:
        score += 6
        strengths.append("Remote option fits Selina's location preference.")
    elif location:
        gaps.append("Location may require relocation unless the role is exceptionally relevant.")

    salary_adjustment, salary_note = evaluate_salary_fit(salary)
    score += salary_adjustment
    if salary_note and salary_adjustment > 0:
        strengths.append(salary_note)
    elif salary_note:
        gaps.append(salary_note)
    elif salary:
        gaps.append("Compensation should be checked against the $200K+ market target.")
    else:
        gaps.append("Salary is not provided yet.")

    skill_terms = {
        "economics": "Economist background",
        "economist": "Economist background",
        "market structure": "Market structure expertise",
        "market intelligence": "Market intelligence and research expertise",
        "research": "Research publications and analytical writing",
        "publication": "Research publications",
        "presentation": "Public speaking and executive communication",
        "stakeholder": "Executive communication",
        "quantitative": "Quantitative research education",
        "modeling": "Quantitative and financial modeling",
        "mandarin": "Mandarin language advantage",
        "chinese": "Mandarin language advantage",
        "strategy": "Strategy background",
        "analytics": "Financial analytics",
    }
    for term, signal in skill_terms.items():
        if term in text and signal not in strengths:
            strengths.append(signal)
            keywords.append(term)

    if any(term in text for term in ["rating", "ratings", "credit rating"]):
        gaps.append("May require direct ratings experience, which should be positioned carefully.")
    if any(term in text for term in ["treasury", "fp&a", "fundraising", "portfolio manager"]):
        gaps.append("May require direct operating experience in a specific finance niche.")
    if len(job_description.strip()) < 80:
        gaps.append("Fit score is preliminary because only limited job detail was entered.")

    default_keywords = [
        "market structure",
        "economic research",
        "financial analytics",
        "strategy",
        "executive communication",
    ]
    for keyword in default_keywords:
        if keyword not in keywords:
            keywords.append(keyword)

    if not strengths:
        strengths.append("Potential fit needs more job description detail.")
    if not gaps:
        gaps.append("No major gaps identified from the information entered.")

    score = max(40, min(score, 96))
    why = (
        "Manually added role. The score is based on the link/details you entered "
        "and Selina's target tiers, location preference, $200K+ compensation target, and background signals."
    )
    return score, tier, strengths[:5], gaps[:4], why, keywords[:8]


def build_custom_job(next_id, title, company, location, salary, link, job_description):
    inferred_title = title_from_url(link)
    inferred_company = infer_company_from_link(link)
    resolved_title = title or inferred_title or "Untitled Role"
    resolved_company = company or inferred_company or "Company TBD"
    enriched_description = " ".join(
        [
            job_description,
            resolved_title,
            resolved_company,
            link,
        ]
    )
    score, tier, strengths, gaps, why, keywords = evaluate_custom_job(
        resolved_title, resolved_company, location, salary, enriched_description
    )
    return {
        "id": next_id,
        "title": resolved_title,
        "company": resolved_company,
        "location": location or "Location TBD",
        "salary": salary or "Salary not posted",
        "tier": tier,
        "fit_score": score,
        "link": link or "https://www.linkedin.com/jobs/",
        "source_notes": job_description,
        "strengths": strengths,
        "gaps": gaps,
        "why": why,
        "keywords": keywords,
    }


def build_application_package(job):
    title = job["title"]
    company = job["company"]
    keywords = ", ".join(job["keywords"][:5])

    bullets = [
        f"Translated Cboe market structure, economic research, and trading ecosystem analysis into executive-ready insights relevant to {title}.",
        f"Applied data science and quantitative research experience to identify market drivers, evaluate trading behavior, and communicate implications to senior stakeholders.",
        f"Authored research publications and delivered public presentations that converted technical analysis into clear recommendations for sophisticated audiences.",
        f"Built cross-functional narratives connecting exchange markets, brokerage behavior, financial products, and strategic priorities across finance, product, and research contexts.",
    ]

    cover_letter = f"""
Dear Hiring Team,

I am excited to apply for the {title} role at {company}. My background as a former Cboe economist, data scientist, and quantitative researcher, combined with market structure expertise, research publications, and senior-level communication experience, gives me a strong foundation for turning complex financial information into clear strategy.

What interests me most about this role is the opportunity to connect rigorous analysis with practical business decisions. I have built my career around interpreting markets, explaining sophisticated ideas to varied audiences, and producing research that supports confident action.

I would bring a disciplined analytical lens, strong writing and presentation skills, and a thoughtful understanding of financial markets. While some areas of the role may require deeper direct exposure to a specific operating niche, I am confident in my ability to ramp quickly and translate my research-driven background into measurable value.

Thank you for your consideration. I would welcome the opportunity to discuss how my background can support {company}'s goals.

Sincerely,
Selina Han
""".strip()

    linkedin_message = f"""
Hi [Name], I saw the {title} opening at {company} and was drawn to the mix of {keywords}. My background includes work as a Cboe economist, data scientist, and quantitative researcher, with market structure expertise, publications, and executive-facing communication. If you are open to it, I would appreciate any perspective on the role or the team. Thank you.
""".strip()

    return bullets, cover_letter, linkedin_message


def build_tailored_resume(job):
    title = job["title"]
    company = job["company"]
    keywords = ", ".join(job["keywords"])
    is_morningstar_research = (
        "morningstar" in company.lower()
        or "equity research" in title.lower()
        or "multi asset" in title.lower()
        or "investment research" in job["tier"].lower()
    )

    headline = (
        "Investment Research and Market Structure Leader"
        if is_morningstar_research
        else "Market Structure, Quantitative Research, and Financial Strategy Leader"
    )

    summary_focus = (
        "multi-asset research, equity research leadership, investment strategy, manager and market analysis, "
        "and client-facing research communication"
        if is_morningstar_research
        else "market structure, quantitative research, financial analytics, product strategy, and executive communication"
    )

    selected_experience = [
        "Led market structure and economic research initiatives translating complex trading, liquidity, volatility, and investor behavior questions into practical strategic insights.",
        "Applied data science and quantitative research methods to analyze financial market dynamics, identify drivers, and communicate implications to senior stakeholders.",
        "Produced research publications, market commentary, and executive-facing presentations for sophisticated financial audiences.",
        "Connected exchange-market expertise with broader investment, brokerage, and product strategy questions across financial services.",
    ]

    if is_morningstar_research:
        selected_experience = [
            "Positioned market structure and economic research for investment audiences by translating complex market dynamics into clear implications for asset allocation, research strategy, and client-facing insight.",
            "Applied quantitative research and data science methods to evaluate market behavior, liquidity, volatility, and structural trends across financial markets.",
            "Authored research publications and delivered public presentations that converted technical analysis into accessible, decision-useful investment narratives.",
            "Built cross-market perspectives connecting equities, options, macro signals, investor behavior, and product trends for senior stakeholders.",
            "Brought exchange-side expertise from Cboe into broader investment research questions relevant to multi-asset research leadership.",
        ]

    resume = f"""
SELINA HAN
Chicago, IL | Open to remote | Mandarin

{headline}

SUMMARY
Former Cboe economist, data scientist, and quantitative researcher with deep market structure expertise, research publications, public speaking experience, and a strong ability to translate complex financial-market analysis into senior-level strategy. Targeting {title} at {company}, with emphasis on {summary_focus}.

CORE STRENGTHS
- Market structure and trading ecosystem analysis
- Economic research and quantitative analysis
- Investment and financial-market research
- Data science, modeling, and evidence-based decision support
- Executive communication, public speaking, and research publication
- Product, strategy, and market intelligence across financial services

SELECTED EXPERIENCE
- {selected_experience[0]}
- {selected_experience[1]}
- {selected_experience[2]}
- {selected_experience[3]}
{f"- {selected_experience[4]}" if len(selected_experience) > 4 else ""}

ROLE-SPECIFIC POSITIONING FOR {company.upper()}
- Emphasize fit with: {keywords}.
- Position Cboe experience as a differentiated foundation for understanding market behavior, investor needs, financial products, and research-driven strategy.
- Highlight senior communication: publications, presentations, stakeholder briefings, and ability to explain technical findings to investment and business audiences.
- Address possible gaps by emphasizing fast ramp-up, rigorous research process, and ability to translate adjacent market expertise into the role's investment or business context.

EDUCATION AND RESEARCH
- Quantitative research background through education.
- Research publication and public presentation experience.
- Economist background with applied financial-market expertise.
""".strip()
    return resume


def extract_resume_text(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        reader = PdfReader(uploaded_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except Exception as exc:
        return f"Could not read uploaded PDF automatically: {exc}"


def build_tailored_resume_from_upload(job, resume_text):
    generated_positioning = build_tailored_resume(job)
    original_excerpt = resume_text[:3500] if resume_text else "No resume text extracted."
    return f"""
SELINA HAN
Tailored Resume for {job['title']} at {job['company']}

TARGET POSITIONING
{generated_positioning}

SOURCE RESUME EXCERPT TO PRESERVE AND EDIT
{original_excerpt}

EDITING NOTES
- Keep verified titles, dates, employers, degrees, and publication names from the original resume.
- Move the strongest Cboe market structure, quantitative research, economist, publication, and public-speaking evidence toward the top.
- For this job, prioritize the keywords: {", ".join(job["keywords"])}.
- Remove or reduce detail that does not support this role's research, investment, market structure, data science, or senior communication needs.
""".strip()


def create_resume_pdf(resume_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42,
    )
    styles = getSampleStyleSheet()
    story = []
    for block in resume_text.split("\n\n"):
        safe_block = block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe_block.replace("\n", "<br/>"), styles["BodyText"]))
        story.append(Spacer(1, 10))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def build_networking_messages(job):
    return {
        "Alumni": f"Hi [Name], I found your profile while researching {job['company']} and noticed our shared academic background. I am exploring the {job['title']} role and would value any perspective you might be willing to share about the company or team.",
        "First-degree connection": f"Hi [Name], I am looking at the {job['title']} role at {job['company']}. Given my Cboe economist, data science, quantitative research, and market structure background, it looks highly relevant. Would you be open to a quick perspective or referral if you think there may be a fit?",
        "Second-degree warm intro": f"Hi [Name], I noticed you are connected to [Contact] at {job['company']}. I am interested in the {job['title']} role and think it aligns with my Cboe market structure, economics, and quantitative research background. Would you feel comfortable introducing us?",
        "Recruiter": f"Hi [Name], I am interested in the {job['title']} role at {job['company']}. My background includes Cboe experience as an economist, data scientist, and quantitative researcher, plus market structure expertise, research publications, and senior-level public communication. I would welcome the chance to discuss whether my profile fits the team’s needs.",
        "Hiring manager": f"Hi [Name], I am very interested in the {job['title']} role. My background combines Cboe market structure experience, economics, data science, quantitative research, and public-facing research communication. I am especially interested in how this role connects analysis with strategic decision-making at {job['company']}. I would welcome the opportunity to connect briefly.",
    }


def render_metric_row(jobs):
    new_jobs = len(jobs)
    high_match = sum(job["fit_score"] >= 85 for job in jobs)
    chicago_remote = sum(
        "Chicago" in job["location"] or "Remote" in job["location"] for job in jobs
    )
    tracker = st.session_state.application_tracker
    outreach_tracker = st.session_state.outreach_tracker
    today = date.today()
    followups_due = sum(
        1
        for item in tracker.values()
        if item.get("follow_up_date") and item["follow_up_date"] <= today
    ) + sum(
        1
        for item in outreach_tracker
        if item.get("follow_up_date") and item["follow_up_date"] <= today
    )
    recruiters_waiting = sum(
        1 for item in tracker.values() if item.get("status") == "Recruiter waiting"
    ) + sum(
        1
        for item in outreach_tracker
        if item.get("status") in {"Messaged", "Waiting for reply"}
    )
    interviews = sum(1 for item in tracker.values() if item.get("status") == "Interview")
    in_progress = sum(
        1
        for item in tracker.values()
        if item.get("status") in {"Interested", "Applied", "Recruiter waiting", "Interview"}
    )

    cols = st.columns(7)
    cols[0].metric("New Jobs", new_jobs)
    cols[1].metric("High Match", high_match)
    cols[2].metric("Chicago/Remote", chicago_remote)
    cols[3].metric("Follow-Ups Due", followups_due)
    cols[4].metric("Recruiters Waiting", recruiters_waiting)
    cols[5].metric("Interviews", interviews)
    cols[6].metric("In Progress", in_progress)


def render_application_tracker(job):
    tracker_key = str(job["id"])
    current = st.session_state.application_tracker.setdefault(
        tracker_key,
        {
            "status": "Interested",
            "applied_date": None,
            "follow_up_date": None,
            "notes": "",
        },
    )
    with st.expander("Track Application"):
        status_options = [
            "Interested",
            "Applied",
            "Recruiter waiting",
            "Interview",
            "Offer",
            "Rejected",
            "Archived",
        ]
        status = st.selectbox(
            "Status",
            status_options,
            index=status_options.index(current.get("status", "Interested")),
            key=f"status_{job['id']}",
        )
        col_1, col_2 = st.columns(2)
        with col_1:
            applied_date = st.date_input(
                "Applied date",
                value=current.get("applied_date") or date.today(),
                key=f"applied_date_{job['id']}",
            )
        with col_2:
            follow_up_date = st.date_input(
                "Follow-up date",
                value=current.get("follow_up_date") or date.today(),
                key=f"follow_up_date_{job['id']}",
            )
        notes = st.text_area(
            "Tracking notes",
            value=current.get("notes", ""),
            key=f"tracking_notes_{job['id']}",
            height=100,
        )
        if st.button("Save Tracking", key=f"save_tracking_{job['id']}"):
            application_row = {
                "saved_at": date.today(),
                "company": job["company"],
                "role": job["title"],
                "status": status,
                "applied_date": applied_date,
                "follow_up_date": follow_up_date,
                "fit_score": job["fit_score"],
                "link": job["link"],
                "notes": notes,
            }
            st.session_state.application_tracker[tracker_key] = application_row
            csv_file = append_csv_row("applications.csv", APPLICATION_COLUMNS, application_row)
            saved, message = append_sheet_row(
                "applications",
                APPLICATION_COLUMNS,
                application_row,
            )
            st.success(f"Saved tracking for {job['company']} - {job['title']}.")
            st.info(f"Saved to iCloud CSV: {csv_file}")
            if saved:
                st.info(message)


def render_networking_tracker():
    st.subheader("Networking Tracker")
    st.write(
        "Track LinkedIn messages, alumni outreach, referrals, recruiters, hiring managers, "
        "and follow-up dates."
    )
    with st.form("networking_tracker_form", clear_on_submit=True):
        col_1, col_2 = st.columns(2)
        with col_1:
            contact_name = st.text_input("Contact name")
            company = st.text_input("Company", value="Morningstar")
            contact_role = st.text_input("Contact role", value="SVP")
        with col_2:
            relationship = st.selectbox(
                "Relationship",
                ["First-degree LinkedIn", "Second-degree LinkedIn", "Alumni", "Recruiter", "Hiring manager", "Other"],
            )
            status = st.selectbox(
                "Outreach status",
                ["Messaged", "Waiting for reply", "Replied", "Followed up", "Call scheduled", "No response", "Closed"],
            )
            message_date = st.date_input("Message date", value=date.today())

        follow_up_date = st.date_input("Follow-up date", value=date.today())
        related_job = st.text_input(
            "Related job",
            value="Head of Equity Research, Multi Asset Research",
        )
        notes = st.text_area(
            "Notes",
            value="Sent LinkedIn message after applying. First-degree connection; may not remember me.",
            height=100,
        )
        submitted = st.form_submit_button("Save Outreach")

    if submitted:
        outreach_row = {
            "saved_at": date.today(),
            "contact_name": contact_name or "Unnamed contact",
            "company": company or "Company TBD",
            "contact_role": contact_role,
            "relationship": relationship,
            "status": status,
            "message_date": message_date,
            "follow_up_date": follow_up_date,
            "related_job": related_job,
            "notes": notes,
        }
        st.session_state.outreach_tracker.append(outreach_row)
        csv_file = append_csv_row("outreach.csv", OUTREACH_COLUMNS, outreach_row)
        saved, message = append_sheet_row(
            "outreach",
            OUTREACH_COLUMNS,
            outreach_row,
        )
        st.success(f"Saved outreach to {contact_name or 'contact'} at {company or 'company'}.")
        st.info(f"Saved to iCloud CSV: {csv_file}")
        if saved:
            st.info(message)

    if st.session_state.outreach_tracker:
        st.write("**Saved Outreach**")
        st.dataframe(pd.DataFrame(st.session_state.outreach_tracker), use_container_width=True)


def render_job_card(job):
    with st.container():
        left, right = st.columns([3, 1])
        with left:
            st.subheader(f"#{job['id']} {job['title']}")
            st.caption(f"{job['company']} | {job['location']} | {job['salary']}")
            st.write(job["tier"])
        with right:
            st.metric("Fit Score", f"{job['fit_score']}/100")
            st.link_button("Open Role", job["link"])

        st.write(f"**Why this is worth considering:** {job['why']}")

        render_application_tracker(job)

        with st.expander("Job Details and Score Notes"):
            st.write(f"**Link:** {job['link']}")
            st.write(f"**Tier assigned:** {job['tier']}")
            st.write(f"**Salary read by dashboard:** {job['salary']}")
            if job.get("source_notes"):
                st.write("**Source notes entered**")
                st.write(job["source_notes"])
            else:
                st.write(
                    "No job description was entered. If you only paste a link, the dashboard "
                    "can infer the company/title from some URLs, but it cannot evaluate the full job detail yet."
                )

        strengths_col, gaps_col = st.columns(2)
        with strengths_col:
            st.write("**Strength Signals**")
            for strength in job["strengths"]:
                st.write(f"- {strength}")
        with gaps_col:
            st.write("**Possible Gaps**")
            for gap in job["gaps"]:
                st.write(f"- {gap}")

        with st.expander("Generate Application"):
            bullets, cover_letter, linkedin_message = build_application_package(job)
            st.write("**Tailored Resume PDF**")
            uploaded_resume = st.file_uploader(
                "Upload your current resume PDF",
                type=["pdf"],
                key=f"resume_upload_{job['id']}",
            )
            if uploaded_resume is not None:
                resume_text = extract_resume_text(uploaded_resume)
                tailored_resume_text = build_tailored_resume_from_upload(job, resume_text)
                resume_pdf = create_resume_pdf(tailored_resume_text)
                st.download_button(
                    "Download Tailored Resume PDF",
                    data=resume_pdf,
                    file_name=f"Selina_Han_Tailored_Resume_{job['company'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"resume_download_{job['id']}",
                )
                st.caption(
                    "This creates an editable starting point in PDF form. Review dates, titles, "
                    "metrics, and exact wording before submitting."
                )
            else:
                st.info("Upload your current resume PDF to generate a tailored resume PDF for this job.")

            st.write("**Tailored Resume Bullets**")
            for bullet in bullets:
                st.write(f"- {bullet}")

            st.write("**Cover Letter Draft**")
            st.text_area(
                "Cover letter",
                cover_letter,
                height=260,
                key=f"cover_letter_{job['id']}",
                label_visibility="collapsed",
            )

            st.write("**LinkedIn Outreach Message**")
            st.text_area(
                "LinkedIn message",
                linkedin_message,
                height=130,
                key=f"linkedin_{job['id']}",
                label_visibility="collapsed",
            )

            st.write("**Keywords to Include**")
            st.write(", ".join(job["keywords"]))

        with st.expander("Generate Networking Plan"):
            st.info(
                "Exact LinkedIn alumni, first-degree, and second-degree counts require "
                "LinkedIn search results, screenshots, exported connection data, or a future integration."
            )
            messages = build_networking_messages(job)
            for audience, message in messages.items():
                st.write(f"**{audience}**")
                st.text_area(
                    audience,
                    message,
                    height=100,
                    key=f"network_{job['id']}_{audience}",
                    label_visibility="collapsed",
                )


def render_job_intake(existing_jobs):
    st.subheader("Add a Job You Found")
    st.write(
        "Paste a job link and add whatever details you have. The dashboard will "
        "score it and add the same application and networking tools."
    )

    with st.form("manual_job_form", clear_on_submit=True):
        col_1, col_2 = st.columns(2)
        with col_1:
            title = st.text_input("Job title")
            company = st.text_input("Company")
            location = st.text_input("Location or remote status")
        with col_2:
            salary = st.text_input("Salary or range")
            link = st.text_input("Job link")
            source = st.selectbox(
                "Source",
                [
                    "LinkedIn saved job",
                    "LinkedIn alert email",
                    "Indeed",
                    "Email",
                    "Company site",
                    "Recruiter",
                    "Other",
                ],
            )

        job_description = st.text_area(
            "Job description or notes",
            height=160,
            placeholder="Paste the job description, recruiter note, or your quick thoughts here.",
        )
        fetch_from_link = st.checkbox(
            "Fetch job details from link",
            value=True,
            help="Works best for company career pages. LinkedIn and Indeed may block automatic reading.",
        )
        submitted = st.form_submit_button("Add and Score Job")

    if submitted:
        next_id = max(job["id"] for job in existing_jobs + st.session_state.custom_jobs) + 1
        fetch_status = ""
        fetched_text = ""
        fetched_details = {}
        if fetch_from_link and link:
            fetched_text, fetch_status = fetch_job_page(link)
            if fetched_text:
                fetched_details = extract_job_details_from_page(link, fetched_text)

        resolved_title = title or fetched_details.get("title", "")
        resolved_company = company or fetched_details.get("company", "")
        resolved_location = location or fetched_details.get("location", "")
        resolved_salary = salary or fetched_details.get("salary", "")
        fetched_requirements = fetched_details.get("requirements", "")
        combined_description = "\n\n".join(
            part
            for part in [
                f"Source: {source}",
                f"Fetch status: {fetch_status}" if fetch_status else "",
                job_description,
                "Fetched requirements/text:",
                fetched_requirements,
            ]
            if part
        )

        new_job = build_custom_job(
            next_id=next_id,
            title=resolved_title,
            company=resolved_company,
            location=resolved_location,
            salary=resolved_salary,
            link=link,
            job_description=combined_description,
        )
        st.session_state.custom_jobs.append(new_job)
        csv_file = append_csv_row("jobs.csv", JOB_COLUMNS, serialize_job(new_job))
        st.success(f"Added {new_job['company']} - {new_job['title']} with a fit score of {new_job['fit_score']}/100.")
        st.info(f"Saved to iCloud CSV: {csv_file}")
        if fetch_status:
            st.info(fetch_status)


def render_phase_one_sources():
    st.subheader("Phase 1 Job Sources")
    st.write(
        "Use these as the first daily inputs. Open a source, save or copy strong jobs, "
        "then paste the job link into the intake box above."
    )

    source_cols = st.columns(4)
    for index, (label, url) in enumerate(SOURCE_LINKS.items()):
        source_cols[index % 4].link_button(label, url)

    st.write("**Reusable search queries**")
    query_cols = st.columns(2)
    for index, query in enumerate(SEARCH_QUERIES):
        linkedin_url = (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={quote_plus(query)}&location={quote_plus('Chicago, Illinois, United States')}"
        )
        indeed_url = (
            "https://www.indeed.com/jobs"
            f"?q={quote_plus(query)}&l={quote_plus('Chicago, IL')}"
        )
        with query_cols[index % 2]:
            st.write(query)
            col_a, col_b = st.columns(2)
            col_a.link_button("LinkedIn", linkedin_url)
            col_b.link_button("Indeed", indeed_url)

    with st.expander("Company Career Pages"):
        for company, url in CAREER_PAGES.items():
            st.link_button(company, url)


def render_google_sheets_status():
    st.subheader("Google Sheets Storage")
    if google_sheets_configured():
        st.success("Google Sheets is configured. Applications and outreach will save to the sheet.")
        try:
            sheet = get_google_sheet()
            get_or_create_worksheet(sheet, "applications", APPLICATION_COLUMNS)
            get_or_create_worksheet(sheet, "outreach", OUTREACH_COLUMNS)
            st.caption("Tabs ready: applications, outreach")
        except Exception as exc:
            st.warning(f"Google Sheets configuration was found, but connection failed: {exc}")
    else:
        st.info(
            "Google Sheets is not configured yet. Add your service account credentials and "
            "Google Sheet ID to Streamlit secrets to save across devices."
        )


def render_icloud_storage_status():
    st.subheader("iCloud CSV Storage")
    folder = ensure_icloud_storage()
    st.success("Local iCloud storage is active.")
    st.caption(str(folder))
    for filename in ["jobs.csv", "applications.csv", "outreach.csv"]:
        path = csv_path(filename)
        if path.exists():
            st.write(f"{filename}: saved")
        else:
            st.write(f"{filename}: will be created when first saved")


if "custom_jobs" not in st.session_state:
    st.session_state.custom_jobs = [
        deserialize_job(row) for row in load_csv_records("jobs.csv", JOB_COLUMNS)
    ]
if "application_tracker" not in st.session_state:
    st.session_state.application_tracker = {}
if "outreach_tracker" not in st.session_state:
    st.session_state.outreach_tracker = load_csv_records("outreach.csv", OUTREACH_COLUMNS)


st.title("Selina Opportunity Dashboard")
st.caption(f"Morning control center | {date.today().strftime('%B %d, %Y')}")

st.write(
    "Daily view for brokerage, exchanges, market structure, prediction markets, "
    "investment research, financial services consulting, and Mandarin-relevant roles."
)

all_jobs = JOBS + st.session_state.custom_jobs

render_metric_row(all_jobs)

st.divider()

render_job_intake(JOBS)

st.divider()

render_phase_one_sources()

st.divider()

render_icloud_storage_status()

st.divider()

render_google_sheets_status()

st.divider()

render_networking_tracker()

st.divider()

saved_application_rows = load_csv_records("applications.csv", APPLICATION_COLUMNS)

if st.session_state.application_tracker or saved_application_rows:
    st.subheader("Application Tracker")
    tracker_rows = []
    job_lookup = {str(job["id"]): job for job in all_jobs}
    for job_id, tracking in st.session_state.application_tracker.items():
        job = job_lookup.get(job_id)
        if not job:
            continue
        tracker_rows.append(
            {
                "Company": job["company"],
                "Role": job["title"],
                "Status": tracking.get("status", ""),
                "Applied Date": tracking.get("applied_date"),
                "Follow-Up Date": tracking.get("follow_up_date"),
                "Notes": tracking.get("notes", ""),
            }
        )
    if tracker_rows:
        st.dataframe(pd.DataFrame(tracker_rows), use_container_width=True)
    if saved_application_rows:
        st.write("**Saved in iCloud CSV**")
        st.dataframe(pd.DataFrame(saved_application_rows), use_container_width=True)
    st.divider()

with st.sidebar:
    st.header("Target Profile")
    st.write("**Location:** Chicago first, remote second")
    st.write("**Market salary target:** $200K+")
    st.write("**Experience:** Senior, 5+ to 10+ years when relevant")
    st.write("**Industries:** Brokerage, exchanges, asset management, FinTech, consulting")
    st.write("**Background signals**")
    for signal in BACKGROUND_SIGNALS:
        st.write(f"- {signal}")

    st.header("Target Companies")
    for category, companies in TARGET_COMPANIES.items():
        st.write(f"**{category}**")
        st.write(", ".join(companies))

    st.header("Filters")
    min_score = st.slider("Minimum fit score", 0, 100, 75, 5)
    selected_tiers = st.multiselect(
        "Role tiers",
        ["Tier 1", "Tier 2", "Tier 3"],
        default=["Tier 1", "Tier 2", "Tier 3"],
    )


filtered_jobs = [
    job
    for job in all_jobs
    if job["fit_score"] >= min_score
    and any(job["tier"].startswith(tier) for tier in selected_tiers)
]

score_df = pd.DataFrame(
    [
        {
            "Role": f"{job['company']} - {job['title']}",
            "Fit Score": job["fit_score"],
            "Salary": job["salary"],
            "Location": job["location"],
        }
        for job in filtered_jobs
    ]
)

if st.session_state.custom_jobs:
    st.subheader("Jobs You Added")
    st.caption("These stay visible even when they are below the minimum score filter.")
    for job in sorted(
        st.session_state.custom_jobs,
        key=lambda item: item["fit_score"],
        reverse=True,
    ):
        render_job_card(job)

    st.divider()

if not filtered_jobs:
    st.warning("No roles match the current filters.")
else:
    st.subheader("Top Recommended Opportunities")
    st.bar_chart(score_df.set_index("Role")["Fit Score"])

    for job in sorted(filtered_jobs, key=lambda item: item["fit_score"], reverse=True):
        render_job_card(job)
