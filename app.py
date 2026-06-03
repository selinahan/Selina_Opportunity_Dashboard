from datetime import date

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Selina Opportunity Dashboard",
    page_icon="💼",
    layout="wide",
)


BACKGROUND_SIGNALS = [
    "Economist background",
    "Market structure expertise",
    "Public speaking and executive communication",
    "Research publications",
    "Quantitative research education",
    "Mandarin language advantage when relevant",
]


JOBS = [
    {
        "id": 1,
        "title": "Director, Commercial Finance",
        "company": "Circana",
        "location": "Remote or Hybrid, Chicago",
        "salary": "$150K-$175K + bonus",
        "tier": "Tier 1: Financial Analytics / Product Strategy / Market Intelligence adjacent",
        "fit_score": 91,
        "link": "https://www.builtinchicago.org/job/director-commercial-finance/9202510",
        "strengths": [
            "Strong match for economics, analytics, and business narrative.",
            "Role values senior stakeholder influence and executive communication.",
            "Chicago/remote-friendly with compensation above the $150K floor.",
        ],
        "gaps": [
            "More FP&A/commercial finance than pure investment strategy.",
            "Resume should show forecasting, budgeting, KPI, and planning-system exposure.",
        ],
        "why": "Best balance of Chicago/remote, seniority, finance, analytics, product support, and executive storytelling.",
        "keywords": [
            "commercial finance",
            "financial planning",
            "forecasting",
            "KPI analysis",
            "executive communication",
            "business narrative",
            "pricing strategy",
        ],
    },
    {
        "id": 2,
        "title": "Director of Capital Markets & Investor Relations",
        "company": "Formic",
        "location": "Remote, U.S.; Chicago company presence",
        "salary": "$150K-$180K",
        "tier": "Tier 1: Investment Strategist / Product Strategy / Financial Analytics",
        "fit_score": 88,
        "link": "https://www.builtinchicago.org/job/director-strategic-finance-investor-relations/8579168",
        "strengths": [
            "Strong capital markets, investor narrative, and strategy alignment.",
            "Research/public speaking background maps well to board and investor materials.",
            "Market and competitive analysis are central to the role.",
        ],
        "gaps": [
            "May expect direct investment banking, PE, VC, structured finance, or fundraising experience.",
            "Application should translate market expertise into capital-formation language.",
        ],
        "why": "A strong strategy-and-finance role where complex market communication could stand out.",
        "keywords": [
            "capital markets",
            "investor relations",
            "financial modeling",
            "board materials",
            "market analysis",
            "capital strategy",
            "KPI framework",
        ],
    },
    {
        "id": 3,
        "title": "Director, Centralized Investment Management Platform",
        "company": "Hightower",
        "location": "Chicago",
        "salary": "$150K-$170K",
        "tier": "Tier 3: Wealth Strategy / Family Office / Investment Platform",
        "fit_score": 86,
        "link": "https://www.ziprecruiter.com/c/hightower/Job/Director%2C-Centralized-Investment-Management-Platform/-in-Chicago%2CIL?jid=3903d6cb43026f4e",
        "strengths": [
            "Close to wealth strategy and investment platform interests.",
            "Market structure and economist lens can support investment-platform strategy.",
            "Chicago location is ideal.",
        ],
        "gaps": [
            "May require direct wealth management platform or advisor-facing experience.",
            "Application should emphasize investment research, client-facing communication, and platform strategy.",
        ],
        "why": "A practical Chicago-based path into wealth strategy and investment-platform leadership.",
        "keywords": [
            "investment management",
            "wealth strategy",
            "advisor platform",
            "portfolio analytics",
            "family office",
            "investment research",
        ],
    },
    {
        "id": 4,
        "title": "Senior Quantitative Researcher, Futures",
        "company": "Undisclosed / eFinancialCareers listing",
        "location": "Remote",
        "salary": "$150K-$300K",
        "tier": "Tier 2: Quantitative Research",
        "fit_score": 82,
        "link": "https://www.efinancialcareers.com/jobs-USA-PA-Radnor-Senior_Quantitative_Researcher_Futures_-_Remote.id24168172",
        "strengths": [
            "Strong conceptual alignment with markets and quantitative research education.",
            "Market structure expertise is relevant for futures and systematic strategy work.",
        ],
        "gaps": [
            "Likely expects direct systematic trading, futures, HFT, or production quant experience.",
            "Resume should include technical methods, datasets, models, and measurable research outputs.",
        ],
        "why": "High-upside role, but best treated as a stretch unless the technical resume is strong.",
        "keywords": [
            "quantitative research",
            "futures",
            "systematic trading",
            "statistical modeling",
            "market microstructure",
            "portfolio optimization",
        ],
    },
    {
        "id": 5,
        "title": "Finance Director, Treasury, Capital Markets & Corporate Finance",
        "company": "Aon",
        "location": "Chicago",
        "salary": "$150K-$190K",
        "tier": "Tier 1: Financial Analytics / Investment Strategy adjacent",
        "fit_score": 80,
        "link": "https://www.glassdoor.com/job-listing/finance-director-treasury-capital-markets-and-corporate-finance-aon-JV_IC1128808_KO0%2C63_KE64%2C67.htm?jl=1010095190457",
        "strengths": [
            "Capital structure and scenario analysis align with economist and market expertise.",
            "Chicago location and compensation fit the target.",
        ],
        "gaps": [
            "Likely wants direct treasury and corporate-finance leadership.",
            "Application should show CFO-facing work, financial modeling, and strategic recommendations.",
        ],
        "why": "Relevant Chicago finance leadership role with a capital markets angle.",
        "keywords": [
            "treasury",
            "capital markets",
            "corporate finance",
            "scenario analysis",
            "capital structure",
            "CFO support",
        ],
    },
]


def build_application_package(job):
    title = job["title"]
    company = job["company"]
    keywords = ", ".join(job["keywords"][:5])

    bullets = [
        f"Translated complex market and economic research into executive-ready insights supporting strategy, risk assessment, and decision-making relevant to {title}.",
        f"Applied quantitative research training and market structure expertise to identify key drivers, interpret data, and communicate implications to senior stakeholders.",
        f"Authored research publications and delivered public presentations that converted technical analysis into clear recommendations for sophisticated audiences.",
        f"Built cross-functional narratives connecting market trends, financial indicators, and strategic priorities across finance, product, and research contexts.",
    ]

    cover_letter = f"""
Dear Hiring Team,

I am excited to apply for the {title} role at {company}. My background as an economist, combined with market structure expertise, quantitative research training, research publications, and senior-level communication experience, gives me a strong foundation for turning complex financial information into clear strategy.

What interests me most about this role is the opportunity to connect rigorous analysis with practical business decisions. I have built my career around interpreting markets, explaining sophisticated ideas to varied audiences, and producing research that supports confident action.

I would bring a disciplined analytical lens, strong writing and presentation skills, and a thoughtful understanding of financial markets. While some areas of the role may require deeper direct exposure to a specific operating niche, I am confident in my ability to ramp quickly and translate my research-driven background into measurable value.

Thank you for your consideration. I would welcome the opportunity to discuss how my background can support {company}'s goals.

Sincerely,
Selina Han
""".strip()

    linkedin_message = f"""
Hi [Name], I saw the {title} opening at {company} and was drawn to the mix of {keywords}. My background is in economics, market structure, quantitative research, publications, and executive-facing communication. If you are open to it, I would appreciate any perspective on the role or the team. Thank you.
""".strip()

    return bullets, cover_letter, linkedin_message


def build_networking_messages(job):
    return {
        "Alumni": f"Hi [Name], I found your profile while researching {job['company']} and noticed our shared academic background. I am exploring the {job['title']} role and would value any perspective you might be willing to share about the company or team.",
        "First-degree connection": f"Hi [Name], I am looking at the {job['title']} role at {job['company']}. Given my economics, market structure, and research background, it looks highly relevant. Would you be open to a quick perspective or referral if you think there may be a fit?",
        "Second-degree warm intro": f"Hi [Name], I noticed you are connected to [Contact] at {job['company']}. I am interested in the {job['title']} role and think it aligns with my economics, market structure, and research background. Would you feel comfortable introducing us?",
        "Recruiter": f"Hi [Name], I am interested in the {job['title']} role at {job['company']}. My background includes economics, market structure expertise, quantitative research education, research publications, and senior-level public communication. I would welcome the chance to discuss whether my profile fits the team’s needs.",
        "Hiring manager": f"Hi [Name], I am very interested in the {job['title']} role. My background combines economics, market structure, quantitative research training, and public-facing research communication. I am especially interested in how this role connects analysis with strategic decision-making at {job['company']}. I would welcome the opportunity to connect briefly.",
    }


def render_metric_row():
    new_jobs = len(JOBS)
    high_match = sum(job["fit_score"] >= 85 for job in JOBS)
    chicago_remote = sum("Chicago" in job["location"] or "Remote" in job["location"] for job in JOBS)

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


st.title("Selina Opportunity Dashboard")
st.caption(f"Morning control center | {date.today().strftime('%B %d, %Y')}")

st.write(
    "Daily view for senior finance, market intelligence, investment strategy, "
    "AI-in-finance, quantitative research, wealth strategy, and Mandarin-relevant roles."
)

render_metric_row()

st.divider()

with st.sidebar:
    st.header("Target Profile")
    st.write("**Location:** Chicago first, remote second")
    st.write("**Salary floor:** $150K")
    st.write("**Experience:** Senior, 5+ to 10+ years when relevant")
    st.write("**Industries:** Finance, FinTech, adjacent high-fit sectors")
    st.write("**Background signals**")
    for signal in BACKGROUND_SIGNALS:
        st.write(f"- {signal}")

    st.header("Filters")
    min_score = st.slider("Minimum fit score", 0, 100, 75, 5)
    selected_tiers = st.multiselect(
        "Role tiers",
        ["Tier 1", "Tier 2", "Tier 3"],
        default=["Tier 1", "Tier 2", "Tier 3"],
    )


filtered_jobs = [
    job
    for job in JOBS
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
