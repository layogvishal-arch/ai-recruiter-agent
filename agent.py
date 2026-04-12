"""
AI Recruiter Agent — Candidate Qualification Engine

Run: python agent.py
"""

import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"


# ══════════════════════════════════════════════
# CANDIDATE DATA (pre-parsed from resume)
# ══════════════════════════════════════════════

RESUME_DATA = {
    "name": "Vishal Goyal",
    "phone": "+91 9611816024",
    "email": "vishallayog@gmail.com",
    "location": "Bengaluru, Karnataka",
    "education": [
        {"institution": "Presidency College", "degree": "BCA", "period": "Jun 2016 – May 2019"},
        {"institution": "Upraised", "degree": "Product Management Fellowship", "period": "Jul 2023 – Nov 2023"},
        {"institution": "LinkedIn Learning", "degree": "Generative AI for Product Managers", "period": "Jan 2024"},
        {"institution": "LinkedIn Learning", "degree": "MongoDB Aggregation Pipeline", "period": "Jan 2025"},
    ],
    "experience": [
        {
            "company": "Tech Mahindra",
            "client": "ServiceNow",
            "role": "Product Lead / Senior Inbound Product Manager",
            "period": "Sep 2025 – Present",
            "type": "Remote",
            "achievements": [
                "Defined and prioritized product roadmap for Task Mining for two quarters",
                "Drove cross-product integration within ServiceNow for SKU bundling and cross-selling",
                "Delivered Automation Center integration with Task Mining, introducing AI-driven solutions",
                "Set Agentic AI scope for next two quarters",
                "Led cross-functional teams with majority based in Prague",
                "Led customer-facing demos and created product documentation/videos",
                "Completed end-to-end UAT for enterprise-scale release despite joining mid-cycle",
            ],
        },
        {
            "company": "HireQuotient",
            "role": "Product Manager",
            "period": "Nov 2023 – Aug 2025",
            "type": "Hybrid",
            "achievements": [
                "Boosted user engagement by 4x (30 to 120 mins)",
                "Achieved 95% accuracy in production by refining OpenAI prompts",
                "Drove $1.2M in ARR through LinkedIn outreach, talent intelligence, ATS integrations",
                "Introduced Hiring Manager collaboration module adding $50K revenue",
                "Reduced funnel drop-offs by 90%",
                "Improved outreach accuracy from 20% to 77%",
                "Cut data costs by 95% and boosted platform stability 10x",
                "Designed GenAI-powered Copilot workflow",
                "Engineered LinkedIn outreach optimization to bypass automation detection",
                "Shipped self-serve analytics dashboard",
            ],
        },
        {
            "company": "Labra.io",
            "role": "Software Engineer",
            "period": "Oct 2022 – Jun 2023",
            "type": "On-site",
            "achievements": [
                "Built notification system reducing debugging time by 25%",
                "Integrated Azure OAuth2 expanding reach to 20% new customers",
                "Applied auto-refreshing credential tokens reducing downtime by 50%",
            ],
        },
        {
            "company": "Inviz AI Solutions",
            "role": "Software Development Engineer",
            "period": "Feb 2022 – Sep 2022",
            "type": "On-site",
            "achievements": [
                "Implemented search features using Algolia for Tata Cliq",
                "Conducted functional testing, resolved 50+ P1/P2 tickets",
            ],
        },
        {
            "company": "Deloitte Consulting USI",
            "client": "HP",
            "role": "Associate Analyst",
            "period": "Aug 2019 – Sep 2021",
            "type": "On-site",
            "achievements": [
                "Resolved 150+ production tickets monthly",
                "Performed UAT for new releases with 98% accuracy",
                "Streamlined incident management: 20% productivity increase, 15% reliability improvement",
                "Trained 4 junior engineers, 30% team efficiency increase",
            ],
        },
    ],
    "skills": {
        "product": ["PRD", "User Research", "Strategic Planning", "Competition Research",
                     "Cross-Functional Collaboration", "Product Roadmap", "Wireframing",
                     "User Stories", "Agile", "Scrum", "MVPs", "Release Plans"],
        "data": ["MongoDB", "SQL", "Excel", "Hotjar", "Mixpanel"],
        "tools": ["Postman", "Whimsical", "Jira", "Intercom", "Figma", "Monday",
                  "Twilio", "MailChimp", "Confluence", "Slack", "ChatGPT", "Claude", "Claude Code"],
        "programming": ["Python", "APIs", "JSON", "Jupyter"],
    },
}


# ══════════════════════════════════════════════
# MOCK TOOLS (swappable with real APIs later)
# ══════════════════════════════════════════════

COMPANY_INTELLIGENCE = {
    "Tech Mahindra": {
        "type": "Service-based IT company",
        "glassdoor_rating": 3.8,
        "employees": "10,000+",
        "stage": "Public / Enterprise",
        "notes": "Candidate worked for ServiceNow as client. The Senior Inbound Product Manager was an IC role directly with ServiceNow's Product Director. He was interviewed and selected by ServiceNow's product team for this role. ServiceNow requires minimum 5 years experience for direct hire at this level.",
        "linkedin_recommendations": [
            {
                "from": "VP of Product, ServiceNow",
                "text": "Few people ramp up as quickly and effectively as Vishal. From day one, he brought a level of diligence and intellectual curiosity that set him apart. Rather than waiting for context, he proactively sought out the right people, asked sharp questions, and invested effort to deeply understand unfamiliar processes. He drove outcomes that moved the needle on product goals well before anyone would have expected. His ability to connect dots across teams and translate complexity into clear direction made him a force multiplier. Where ambiguity and shifting priorities can stall even experienced PMs, Vishal leaned in with resilience and professionalism. I'd welcome the chance to work with him again in a heartbeat.",
            },
            {
                "from": "Director of Product, ServiceNow",
                "text": "Vishal stands out for his sharp analytical thinking and ability to quickly grasp even highly complex products. He brings a rare combination of engineering depth and product expertise. His technical understanding allows him to navigate constraints with confidence, while his product mindset ensures decisions remain aligned with long-term goals. He carefully balances user experience with strategic objectives. Working with him is both productive and genuinely enjoyable.",
            },
            {
                "from": "Staff Engineer, ServiceNow",
                "text": "Vishal has a sharp eye for product detail and a strong sense of priorities, which made it easy for the development team to stay aligned and focused. He communicated requirements with clarity, coordinated across functions seamlessly, and drove execution with precision. I would highly recommend Vishal to any team looking for a PM who combines strategic thinking with strong delivery.",
            },
        ],
    },
    "HireQuotient": {
        "type": "HRtech AI startup",
        "glassdoor_rating": 4.0,
        "employees": "10-50",
        "stage": "Pre-seed",
        "funding": "$1.8M USD (2022)",
        "founder_background": "IIT Delhi",
        "pm_history": "7 PMs from 2022-2026. All others left before 1 year. Head of Product joined after Vishal, left before Vishal. Vishal left as the last PM — longest PM tenure in company history.",
        "notes": "High PM turnover indicates either challenging environment or rapid pivoting. Vishal's longest tenure suggests strong resilience, ownership, and trust from leadership.",
        "social_proof": "Founder has publicly spoken about and tagged Vishal on LinkedIn during partnership announcements, indicating strong founder-PM relationship and public recognition.",
        "linkedin_recommendations": [
            {
                "from": "Full Stack Engineer, HireQuotient",
                "text": "Vishal is one of the most meticulous and detail oriented person I have worked with. His research oriented mindset and way of working is second to none. I remember working with him on several important impactful customer facing solutions and the way he researched and found the most optimal solutions to solving product and feature problems is absolutely incredible. His approach to customer oriented solutions has enabled teams to deliver impactful products at HireQuotient.",
            },
        ],
    },
    "Labra.io": {
        "type": "AI-native engineering company",
        "glassdoor_rating": None,
        "employees": "10-50",
        "stage": "Early stage",
        "focus": "Cloud GTM, CRMs",
    },
    "Inviz AI Solutions": {
        "type": "Search-based solutions",
        "glassdoor_rating": 2.7,
        "employees": "10-50",
        "stage": "Early stage",
    },
    "Deloitte Consulting USI": {
        "type": "Service-based consulting",
        "glassdoor_rating": 4.0,
        "employees": "10,000+",
        "stage": "Public / Enterprise",
        "notes": "Candidate worked at HP as client, in support and engineering team.",
    },
}


# ── Tool functions (the agent calls these) ──

def tool_get_resume() -> dict:
    """Returns the full parsed resume data."""
    return RESUME_DATA


def tool_get_company_intel(company_name: str) -> dict:
    """Returns company intelligence for a given company."""
    for key in COMPANY_INTELLIGENCE:
        if key.lower() in company_name.lower() or company_name.lower() in key.lower():
            return {"company": key, **COMPANY_INTELLIGENCE[key]}
    return {"company": company_name, "error": "No intelligence data available for this company"}


def tool_get_all_companies_intel() -> list:
    """Returns intelligence for all companies in the candidate's history."""
    results = []
    for exp in RESUME_DATA["experience"]:
        intel = tool_get_company_intel(exp["company"])
        intel["candidate_role"] = exp["role"]
        intel["candidate_period"] = exp["period"]
        results.append(intel)
    return results


# ── Tool registry (maps tool names to functions) ──

TOOL_FUNCTIONS = {
    "get_resume": tool_get_resume,
    "get_company_intel": tool_get_company_intel,
    "get_all_companies_intel": tool_get_all_companies_intel,
}

# ── Tool definitions for Claude API ──

TOOLS = [
    {
        "name": "get_resume",
        "description": "Get the full parsed resume data for the candidate including education, experience, skills, and achievements.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_company_intel",
        "description": "Get company intelligence data including glassdoor rating, company stage, funding, employee count, and special notes. Use this to assess the quality and context of a candidate's work experience at a specific company.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Name of the company to look up",
                },
            },
            "required": ["company_name"],
        },
    },
    {
        "name": "get_all_companies_intel",
        "description": "Get intelligence data for ALL companies in the candidate's work history at once. Returns company stage, ratings, funding, and contextual notes for each employer.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# ══════════════════════════════════════════════
# AGENT CORE
# ══════════════════════════════════════════════

SYSTEM_PROMPT = """You are an expert AI recruiter agent that qualifies candidates for job positions.

You have access to tools to retrieve candidate data and company intelligence. USE THE TOOLS — do not make assumptions about the candidate without first fetching their data.

YOUR PROCESS:
1. First, call get_resume to get the candidate's full profile
2. Then, call get_all_companies_intel to understand the context of each role
3. Analyze the candidate against the job description and vetting criteria
4. Provide a structured qualification assessment

YOUR OUTPUT FORMAT (after gathering all data):

## Candidate Qualification Report

### Match Score: [Strong Fit / Potential Fit / Not a Fit]

### JD Requirements Analysis
For each requirement from the JD, assess:
- Requirement: [what the JD asks for]
- Evidence: [specific proof from resume]
- Match: [Met / Partially Met / Not Met]
- Notes: [context from company intelligence that strengthens or weakens the match]

### Vetting Criteria Assessment
For each vetting criterion provided, assess with evidence.

### Company Intelligence Insights
Highlight anything from the company data that adds important context — such as the candidate's tenure relative to peers, company stage relevance, or red flags.

### Strengths (top 3-5)
Backed by specific data points.

### Gaps / Risks (if any)
Be honest about weaknesses.

### Recommendation
Clear hire/no-hire recommendation with reasoning.

### Outreach Draft
If the candidate is a Strong Fit or Potential Fit, draft a cold email that:
- References specific achievements from their background
- Connects their experience to the JD
- Is personalized, not generic
- Is concise (under 150 words)

If Not a Fit, explain why and skip the outreach.

IMPORTANT:
- Always cite specific numbers, achievements, and data points from the resume
- Use company intelligence to add depth (e.g., "lasted longest among 7 PMs" is more meaningful than "worked for 2 years")
- Be direct and opinionated — recruiters want a clear recommendation, not hedging
- If a vetting criterion cannot be assessed with available data, say so explicitly
"""


def run_agent(jd: str, vetting_criteria: list) -> str:
    """
    Run the recruiter agent with tool-use loop.
    
    The agent:
    1. Receives JD + vetting criteria
    2. Decides which tools to call
    3. Calls tools, receives results
    4. Reasons about the data
    5. Produces the qualification report
    
    This uses Claude's native tool_use — the model decides
    which tools to call and when, not hardcoded logic.
    """
    client = anthropic.Anthropic()
    
    # Format vetting criteria
    criteria_text = ""
    if vetting_criteria:
        criteria_text = "\n\nADDITIONAL VETTING CRITERIA:\n"
        for i, vc in enumerate(vetting_criteria):
            criteria_text += f"{i+1}. [{vc['type']}] {vc['criteria']}\n"
    
    user_message = f"""Qualify the candidate for the following position.

JOB DESCRIPTION:
{jd}
{criteria_text}

Start by fetching the candidate's resume and company intelligence, then provide your full qualification assessment."""

    messages = [{"role": "user", "content": user_message}]
    
    total_input_tokens = 0
    total_output_tokens = 0
    tool_calls_made = 0
    
    # Agent loop — keeps running until the model stops calling tools
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens
        
        # Check if the model wants to use tools
        if response.stop_reason == "tool_use":
            # Process all tool calls in this response
            assistant_content = response.content
            tool_results = []
            
            for block in assistant_content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id
                    tool_calls_made += 1
                    
                    print(f"  Agent calling tool: {tool_name}({json.dumps(tool_input) if tool_input else ''})")
                    
                    # Execute the tool
                    if tool_name in TOOL_FUNCTIONS:
                        if tool_input:
                            result = TOOL_FUNCTIONS[tool_name](**tool_input)
                        else:
                            result = TOOL_FUNCTIONS[tool_name]()
                    else:
                        result = {"error": f"Unknown tool: {tool_name}"}
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": json.dumps(result, indent=2),
                    })
            
            # Add assistant message and tool results to conversation
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})
            
        else:
            # Model is done — extract final text
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            
            # Cost calculation (Haiku pricing)
            cost = (total_input_tokens * 0.25 / 1_000_000) + (total_output_tokens * 1.25 / 1_000_000)
            
            print(f"\n  --- Agent Stats ---")
            print(f"  Tool calls: {tool_calls_made}")
            print(f"  Input tokens: {total_input_tokens}")
            print(f"  Output tokens: {total_output_tokens}")
            print(f"  Estimated cost: ${cost:.4f}")
            
            return final_text


# ══════════════════════════════════════════════
# INTERACTIVE RUNNER
# ══════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  AI RECRUITER AGENT — Candidate Qualification")
    print("=" * 60)
    
    # Get JD
    print("\nPaste the Job Description (type END on a new line when done):")
    jd_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        jd_lines.append(line)
    jd = "\n".join(jd_lines)
    
    if not jd.strip():
        print("No JD provided. Using default test JD...")
        jd = DEFAULT_JD
    
    # Get vetting criteria
    vetting_criteria = []
    print("\nAdd vetting criteria (or type SKIP to proceed):")
    
    criteria_types = {
        "1": "years of experience",
        "2": "skills",
        "3": "company intelligence",
        "4": "work experience",
    }
    
    while True:
        print("\n  Select type:")
        print("  1. Years of experience")
        print("  2. Skills")
        print("  3. Company intelligence")
        print("  4. Work experience")
        print("  Type SKIP to proceed with current criteria, DONE to finish adding")
        
        choice = input("  > ").strip()
        
        if choice.upper() in ("SKIP", "DONE"):
            break
        
        if choice not in criteria_types:
            print("  Invalid choice, try again")
            continue
        
        criteria_type = criteria_types[choice]
        criteria_text = input(f"  Enter {criteria_type} criteria: ").strip()
        
        if criteria_text:
            vetting_criteria.append({"type": criteria_type, "criteria": criteria_text})
            print(f"  Added: [{criteria_type}] {criteria_text}")
    
    # Run the agent
    print(f"\n{'=' * 60}")
    print(f"  Running agent with {len(vetting_criteria)} vetting criteria...")
    print(f"{'=' * 60}\n")
    
    result = run_agent(jd, vetting_criteria)
    
    print(f"\n{'=' * 60}")
    print(f"  QUALIFICATION REPORT")
    print(f"{'=' * 60}")
    print(result)


# ── Default test JD ──

DEFAULT_JD = """The Role
We're looking for a Founding Product Manager to build and own the product function at Juicebox from the ground up.
This role will be the connective tissue between customers, engineering, design, sales, and customer success teams.

You Will
- Translate customer business needs into clear, comprehensive product requirements (PRDs, specs, tickets)
- Partner closely with engineering and design to lead projects end-to-end
- Act as the primary point of contact for product feedback
- Spend significant time talking directly with customers
- Triage and prioritize bugs vs. features
- Work cross-functionally with sales and customer success
- Help define and guide quarterly product roadmaps
- Establish lightweight but effective product workflows

You Have
- 2+ years of Product Management experience (4-5+ years preferred)
- Experience working in early-stage or high growth startup environments
- Strong prioritization, judgment, and communication skills
- Comfort operating in ambiguity and owning outcomes end-to-end
- Proven ability to translate customer needs into clear product requirements"""


if __name__ == "__main__":
    main()