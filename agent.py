"""
AI Recruiter Agent v2 — Agentic Candidate Qualification

Key difference from v1: Claude decides WHICH tools to call and WHEN.
- Resume is always fetched (baseline data)
- Company intel is fetched per company, only for relevant ones
- Recommendations are fetched only when borderline or need validation
- Social proof is fetched only when assessing culture fit or founder access
- Outreach is drafted only if candidate qualifies

Run: python agent.py
"""

import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"


# ══════════════════════════════════════════════
# DATA STORES (separated by tool)
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

COMPANY_INTEL_DATA = {
    "Tech Mahindra": {
        "type": "Service-based IT company",
        "glassdoor_rating": 3.8,
        "employees": "10,000+",
        "stage": "Public / Enterprise",
        "candidate_context": "Candidate worked for ServiceNow as client. The Senior Inbound PM role was an IC position directly with ServiceNow's Product Director. He was interviewed and selected by ServiceNow's product team. ServiceNow requires minimum 5 years experience for direct hire at this level.",
    },
    "HireQuotient": {
        "type": "HRtech AI startup",
        "glassdoor_rating": 4.0,
        "employees": "10-50",
        "stage": "Pre-seed",
        "funding": "$1.8M USD (2022)",
        "founder_background": "IIT Delhi",
        "candidate_context": "7 PMs from 2022-2026. All others left before 1 year. Head of Product joined after Vishal, left before Vishal. Vishal left as the last PM — longest PM tenure in company history. High PM turnover suggests challenging environment. Vishal's longest tenure indicates strong resilience and trust from leadership.",
    },
    "Labra.io": {
        "type": "AI-native engineering company",
        "glassdoor_rating": None,
        "employees": "10-50",
        "stage": "Early stage",
        "focus": "Cloud GTM, CRMs",
        "candidate_context": "Candidate was a software engineer here, not a PM role.",
    },
    "Inviz AI Solutions": {
        "type": "Search-based solutions",
        "glassdoor_rating": 2.7,
        "employees": "10-50",
        "stage": "Early stage",
        "candidate_context": "Candidate was a software engineer here, not a PM role.",
    },
    "Deloitte Consulting USI": {
        "type": "Service-based consulting",
        "glassdoor_rating": 4.0,
        "employees": "10,000+",
        "stage": "Public / Enterprise",
        "candidate_context": "Candidate worked at HP as client, in support and engineering team. This was an analyst role, pre-PM career.",
    },
}

RECOMMENDATIONS_DATA = {
    "Tech Mahindra": [
        {
            "from": "VP of Product, ServiceNow",
            "relationship": "Direct manager / stakeholder",
            "text": "Few people ramp up as quickly and effectively as Vishal. From day one, he brought a level of diligence and intellectual curiosity that set him apart. Rather than waiting for context, he proactively sought out the right people, asked sharp questions, and invested effort to deeply understand unfamiliar processes. He drove outcomes that moved the needle on product goals well before anyone would have expected. His ability to connect dots across teams and translate complexity into clear direction made him a force multiplier. Where ambiguity and shifting priorities can stall even experienced PMs, Vishal leaned in with resilience and professionalism. I'd welcome the chance to work with him again in a heartbeat.",
        },
        {
            "from": "Director of Product, ServiceNow",
            "relationship": "Direct counterpart",
            "text": "Vishal stands out for his sharp analytical thinking and ability to quickly grasp even highly complex products. He brings a rare combination of engineering depth and product expertise. His technical understanding allows him to navigate constraints with confidence, while his product mindset ensures decisions remain aligned with long-term goals. He carefully balances user experience with strategic objectives. Working with him is both productive and genuinely enjoyable.",
        },
        {
            "from": "Staff Engineer, ServiceNow",
            "relationship": "Engineering partner",
            "text": "Vishal has a sharp eye for product detail and a strong sense of priorities, which made it easy for the development team to stay aligned and focused. He communicated requirements with clarity, coordinated across functions seamlessly, and drove execution with precision. I would highly recommend Vishal to any team looking for a PM who combines strategic thinking with strong delivery.",
        },
    ],
    "HireQuotient": [
        {
            "from": "Full Stack Engineer, HireQuotient",
            "relationship": "Engineering partner",
            "text": "Vishal is one of the most meticulous and detail oriented person I have worked with. His research oriented mindset and way of working is second to none. I remember working with him on several important impactful customer facing solutions and the way he researched and found the most optimal solutions to solving product and feature problems is absolutely incredible. His approach to customer oriented solutions has enabled teams to deliver impactful products at HireQuotient.",
        },
    ],
    "Labra.io": [],
    "Inviz AI Solutions": [],
    "Deloitte Consulting USI": [],
}

SOCIAL_PROOF_DATA = {
    "Tech Mahindra": {
        "public_mentions": None,
        "notable": "Interviewed and selected by ServiceNow's product leadership for a role that typically requires 5+ years. Candidate had ~2 years PM experience at the time.",
    },
    "HireQuotient": {
        "public_mentions": "Founder has publicly spoken about and tagged Vishal on LinkedIn during partnership announcements. This indicates strong founder-PM relationship and public recognition of contributions.",
        "notable": "Longest PM tenure in company history (1.75 years). 6 other PMs left before completing 1 year. Head of Product joined after Vishal and left before him.",
    },
    "Labra.io": {"public_mentions": None, "notable": None},
    "Inviz AI Solutions": {"public_mentions": None, "notable": None},
    "Deloitte Consulting USI": {"public_mentions": None, "notable": None},
}


# ══════════════════════════════════════════════
# TOOL FUNCTIONS
# ══════════════════════════════════════════════

def tool_get_resume() -> dict:
    return RESUME_DATA

def tool_get_company_intel(company_name: str) -> dict:
    for key in COMPANY_INTEL_DATA:
        if key.lower() in company_name.lower() or company_name.lower() in key.lower():
            return {"company": key, **COMPANY_INTEL_DATA[key]}
    return {"company": company_name, "error": "No intelligence data available"}

def tool_get_recommendations(company_name: str) -> dict:
    for key in RECOMMENDATIONS_DATA:
        if key.lower() in company_name.lower() or company_name.lower() in key.lower():
            recs = RECOMMENDATIONS_DATA[key]
            if recs:
                return {"company": key, "recommendations": recs, "count": len(recs)}
            else:
                return {"company": key, "recommendations": [], "count": 0, "note": "No LinkedIn recommendations available for this company"}
    return {"company": company_name, "error": "Company not found"}

def tool_get_social_proof(company_name: str) -> dict:
    for key in SOCIAL_PROOF_DATA:
        if key.lower() in company_name.lower() or company_name.lower() in key.lower():
            return {"company": key, **SOCIAL_PROOF_DATA[key]}
    return {"company": company_name, "error": "No social proof data available"}

TOOL_FUNCTIONS = {
    "get_resume": tool_get_resume,
    "get_company_intel": tool_get_company_intel,
    "get_recommendations": tool_get_recommendations,
    "get_social_proof": tool_get_social_proof,
}


# ══════════════════════════════════════════════
# TOOL DEFINITIONS FOR CLAUDE API
# ══════════════════════════════════════════════

TOOLS = [
    {
        "name": "get_resume",
        "description": "Get the candidate's full parsed resume including education, work experience, skills, and achievements. Always call this first.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_company_intel",
        "description": "Get intelligence data for a SPECIFIC company — glassdoor rating, stage, funding, employee count, and contextual notes about the candidate's role there. Call this only for companies that are RELEVANT to the JD requirements. For example, if the JD requires startup experience, fetch intel for the candidate's startup roles, not for large enterprise employers unless their experience there is relevant to a specific vetting criterion.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Exact company name from the candidate's resume",
                },
            },
            "required": ["company_name"],
        },
    },
    {
        "name": "get_recommendations",
        "description": "Get LinkedIn recommendations from colleagues at a SPECIFIC company. These are direct quotes from people who worked with the candidate. Use this tool ONLY when: (1) your initial assessment on a JD requirement or vetting criterion is borderline and you need peer validation, (2) you need to verify a specific claim about the candidate's working style or impact, or (3) the JD emphasizes soft skills like communication or leadership that are hard to assess from resume bullets alone. Do NOT call this for every company — it's expensive. Call it for at most 2 companies where the recommendations would most influence your decision.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Exact company name to fetch recommendations for",
                },
            },
            "required": ["company_name"],
        },
    },
    {
        "name": "get_social_proof",
        "description": "Get social proof data for a SPECIFIC company — public LinkedIn mentions by founders, notable context about the candidate's tenure relative to peers, and other signals that indicate the candidate's standing beyond resume bullets. Use this ONLY when: (1) a vetting criterion asks about founder access or culture fit, (2) you need to assess the candidate's reputation or standing at a company, or (3) you see unusual patterns in tenure that need context (e.g., very short or very long stay). Do NOT call this routinely.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Exact company name to fetch social proof for",
                },
            },
            "required": ["company_name"],
        },
    },
]


# ══════════════════════════════════════════════
# SYSTEM PROMPT — THE AGENT'S BRAIN
# ══════════════════════════════════════════════

SYSTEM_PROMPT = """You are an expert AI recruiter agent that qualifies candidates for job positions using available tools.

## YOUR REASONING PROCESS

You think step-by-step and make deliberate decisions about what information to gather.

### Step 1: Get the resume (always)
Call get_resume to understand the candidate's background.

### Step 2: Identify relevant companies (your judgment)
Based on the JD and vetting criteria, decide which of the candidate's companies are MOST relevant.
- ALWAYS fetch company intel for the candidate's CURRENT/MOST RECENT role — it reflects their latest capabilities regardless of company type. A candidate at an enterprise company might still be doing startup-relevant IC work.
- Then fetch intel for 1-3 additional companies most relevant to the JD requirements in the most recent order.
- Engineering roles may be less relevant for a PM position unless the JD values technical depth.
Call get_company_intel for the current role + 1-2 most relevant companies. Explain why you chose them.

### Step 3: Form an initial assessment
Before fetching more data, form a preliminary assessment:
- For each JD requirement: Met / Partially Met / Not Met / Cannot Assess
- For each vetting criterion: same assessment
- Identify which assessments are BORDERLINE (could go either way)

### Step 4: Deep dive only where needed (your judgment)
- If an assessment is borderline, call get_recommendations for the relevant company to find supporting or contradicting evidence
- If a vetting criterion mentions founder access or culture fit, call get_social_proof
- If an assessment is clearly Met or clearly Not Met, do NOT fetch more data — you have enough
- NEVER call get_recommendations or get_social_proof for more than 2 companies total

### Step 5: Make your decision
Based on all gathered evidence, provide your final assessment.

CRITICAL — Must-have vs Nice-to-have vetting criteria:
- Vetting criteria marked as [MUST HAVE] are hard disqualifiers. If the candidate does not meet a must-have, the recommendation is "Not a Fit" regardless of other strengths.
- Vetting criteria marked as [NICE TO HAVE] should inform the assessment but should NOT disqualify the candidate on their own. A candidate who misses a nice-to-have but excels everywhere else can still be a Strong Fit.
- When a candidate is borderline on a must-have (within 10-15% of the threshold), flag it as a risk but do not auto-disqualify — let the hiring team decide. For example, 1.75 years vs 2 years required is borderline, not a hard fail.

### Step 6: Conditional outreach
- If Strong Fit: draft a personalized cold email (under 150 words) referencing specific achievements
- If Potential Fit: draft a shorter, more cautious email
- If Not a Fit: do NOT draft outreach. Instead explain why and suggest what type of role would be better suited

## OUTPUT FORMAT

### Candidate Qualification Report

**Tools used:** [list which tools you called and why]

**Match Score:** [Strong Fit / Potential Fit / Not a Fit]

**JD Requirements Analysis:**
For each requirement:
- Requirement → Evidence → Match level → Notes

**Vetting Criteria Assessment:**
For each criterion with evidence.

**Key Strengths (top 3-5):** backed by specific data points

**Gaps / Risks:** be direct about weaknesses

**Recommendation:** clear hire/no-hire with reasoning

**Outreach Draft:** (only if qualified)

## RULES
- Always cite specific numbers and achievements, never be vague
- Use company intelligence to add depth beyond resume bullets
- Be opinionated — recruiters want a clear recommendation, not hedging
- If you cannot assess a criterion with available data, say so explicitly rather than guessing
- Show your reasoning for each tool call decision
"""


# ══════════════════════════════════════════════
# AGENT LOOP
# ══════════════════════════════════════════════

def run_agent(jd: str, vetting_criteria: list) -> str:
    client = anthropic.Anthropic()
    
    criteria_text = ""
    if vetting_criteria:
        criteria_text = "\n\nADDITIONAL VETTING CRITERIA:\n"
        for i, vc in enumerate(vetting_criteria):
            priority = vc.get('priority', 'must have').upper()
            criteria_text += f"{i+1}. [{vc['type']}] [{priority}] {vc['criteria']}\n"
    
    user_message = f"""Qualify the candidate for the following position. Follow your reasoning process step by step. Be deliberate about which tools you call and explain your reasoning.

JOB DESCRIPTION:
{jd}
{criteria_text}

Begin by fetching the candidate's resume, then reason about which companies and data points are most relevant before fetching more."""

    messages = [{"role": "user", "content": user_message}]
    
    total_input_tokens = 0
    total_output_tokens = 0
    tool_calls_log = []
    
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
        
        if response.stop_reason == "tool_use":
            assistant_content = response.content
            tool_results = []
            
            # Print any reasoning text before tool calls
            for block in assistant_content:
                if hasattr(block, "text") and block.text.strip():
                    print(f"\n  Agent thinking: {block.text[:200]}...")
            
            for block in assistant_content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id
                    
                    input_str = json.dumps(tool_input) if tool_input else ""
                    print(f"  → Calling: {tool_name}({input_str})")
                    tool_calls_log.append(f"{tool_name}({input_str})")
                    
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
            
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})
            
        else:
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            
            cost = (total_input_tokens * 0.25 / 1_000_000) + (total_output_tokens * 1.25 / 1_000_000)
            
            print(f"\n  --- Agent Stats ---")
            print(f"  Tool calls made: {len(tool_calls_log)}")
            for i, tc in enumerate(tool_calls_log):
                print(f"    {i+1}. {tc}")
            print(f"  Input tokens: {total_input_tokens}")
            print(f"  Output tokens: {total_output_tokens}")
            print(f"  Estimated cost: ${cost:.4f}")
            
            return final_text


# ══════════════════════════════════════════════
# INTERACTIVE RUNNER
# ══════════════════════════════════════════════

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


def main():
    print("=" * 60)
    print("  AI RECRUITER AGENT v2 — Agentic Qualification")
    print("=" * 60)
    
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
        print("  Type DONE to finish adding criteria")
        
        choice = input("  > ").strip()
        
        if choice.upper() in ("SKIP", "DONE"):
            break
        
        if choice not in criteria_types:
            print("  Invalid choice, try again")
            continue
        
        criteria_type = criteria_types[choice]
        criteria_text = input(f"  Enter {criteria_type} criteria: ").strip()
        
        if criteria_text:
            priority_input = input(f"  Priority — 1. Must have  2. Nice to have: ").strip()
            priority = "nice to have" if priority_input == "2" else "must have"
            vetting_criteria.append({"type": criteria_type, "criteria": criteria_text, "priority": priority})
            print(f"  ✓ Added: [{criteria_type}] [{priority.upper()}] {criteria_text}")
    
    print(f"\n{'=' * 60}")
    print(f"  Running agent with {len(vetting_criteria)} vetting criteria...")
    print(f"  Watch the tool calls below — the agent decides what to fetch.")
    print(f"{'=' * 60}\n")
    
    result = run_agent(jd, vetting_criteria)
    
    print(f"\n{'=' * 60}")
    print(f"  QUALIFICATION REPORT")
    print(f"{'=' * 60}")
    print(result)


if __name__ == "__main__":
    main()