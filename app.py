from datetime import date
import re
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st


SALARY_FLOOR = 200_000


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
    score, tier, strengths, gaps, why, keywords = evaluate_custom_job(
        title, company, location, salary, job_description
    )
    return {
        "id": next_id,
        "title": title or "Untitled Role",
        "company": company or "Company TBD",
        "location": location or "Location TBD",
        "salary": salary or "Salary not posted",
        "tier": tier,
        "fit_score": score,
        "link": link or "https://www.linkedin.com/jobs/",
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

    cols = st.columns(7)
    cols[0].metric("New Jobs", new_jobs)
    cols[1].metric("High Match", high_match)
    cols[2].metric("Chicago/Remote", chicago_remote)
    cols[3].metric("Follow-Ups Due", "0")
    cols[4].metric("Recruiters Waiting", "0")
    cols[5].metric("Interviews", "0")
    cols[6].metric("In Progress", "0")


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
        submitted = st.form_submit_button("Add and Score Job")

    if submitted:
        next_id = max(job["id"] for job in existing_jobs + st.session_state.custom_jobs) + 1
        new_job = build_custom_job(
            next_id=next_id,
            title=title,
            company=company,
            location=location,
            salary=salary,
            link=link,
            job_description=f"{source}. {job_description}",
        )
        st.session_state.custom_jobs.append(new_job)
        st.success(f"Added {new_job['company']} - {new_job['title']} with a fit score of {new_job['fit_score']}/100.")


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


if "custom_jobs" not in st.session_state:
    st.session_state.custom_jobs = []


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

if not filtered_jobs:
    st.warning("No roles match the current filters.")
else:
    st.subheader("Top Recommended Opportunities")
    st.bar_chart(score_df.set_index("Role")["Fit Score"])

    for job in sorted(filtered_jobs, key=lambda item: item["fit_score"], reverse=True):
        render_job_card(job)
