# AI Recruiter Agent — Agentic Candidate Qualification

An AI agent that qualifies job candidates using multi-source intelligence gathering and conditional reasoning. Unlike a simple LLM prompt, this agent decides which data to fetch, when to dig deeper, and when to fast-reject — demonstrating real agentic behavior with tool use.

## What Makes This an Agent (Not Just a Prompt)

| Simple LLM Call | This Agent |
|----------------|-----------|
| Send all data at once, get a report | Fetches data incrementally based on what it needs |
| Same flow every time | Different tool calls for different JDs |
| Processes every candidate the same way | Fast-rejects domain mismatches in 1 tool call |
| No judgment about what info matters | Decides which companies to research and which to skip |
| Always generates outreach | Only drafts outreach if candidate qualifies |

## How It Works

### Agent Flow

```
User provides: JD + Vetting Criteria (must-have / nice-to-have)
                        │
                   ┌────┴────┐
                   │ Step 1  │ Get resume (always)
                   └────┬────┘
                        │
                   ┌────┴────┐
                   │ Step 2  │ Pre-qualification gate
                   └────┬────┘
                   ╱         ╲
            Domain            Domain
            mismatch          relevant
                │                │
         Fast reject        ┌────┴────┐
         (1 tool call)      │ Step 3  │ Fetch company intel
         Match: Not a Fit   └────┬────┘ (agent chooses which companies)
                                 │
                            ┌────┴────┐
                            │ Step 4  │ Initial assessment
                            └────┬────┘
                            ╱         ╲
                     Borderline      Clear
                         │            │
                    ┌────┴────┐       │
                    │ Step 5  │       │
                    │Deep dive│       │ (skip deep dive)
                    └────┬────┘       │
                         ╲          ╱
                          ┌────┴────┐
                          │ Step 6  │ Decision
                          └────┬────┘
                          ╱         ╲
                   Qualified      Not qualified
                       │               │
                  Draft outreach   Explain gaps
```

### Tools Available

| Tool | When Agent Calls It | Decision Logic |
|------|-------------------|----------------|
| `get_resume` | Always, first call | Baseline data needed for any assessment |
| `get_company_intel(company)` | For current role (always) + 1-2 most relevant companies | Agent judges relevance based on JD requirements |
| `get_recommendations(company)` | Only when assessment is borderline and needs peer validation | Max 2 companies — agent decides which ones matter most |
| `get_social_proof(company)` | Only when vetting criteria mention founder access or culture fit | Agent checks if this data would change the decision |

### Vetting Criteria

Each criterion is tagged as **must-have** or **nice-to-have**:

- **Must-have:** Hard disqualifier if not met (with borderline tolerance of 10-15%)
- **Nice-to-have:** Informs assessment but does not disqualify on its own

Categories: years of experience, skills, company intelligence, work experience

## Guardrails

### 1. Domain Mismatch Fast Reject
If the candidate's career domain doesn't match the JD (e.g., Product Manager applying for Data Scientist), the agent immediately returns a short rejection using only 1 tool call instead of 5-6. Saves ~80% cost per rejected candidate.

### 2. Conditional Outreach
Outreach is only drafted for Strong Fit or Potential Fit candidates. Not a Fit candidates receive gap analysis and suggested better-fit roles instead.

### 3. Must-Have vs Nice-to-Have
Nice-to-have criteria that are not met do not auto-disqualify. Only must-have failures trigger rejection, and borderline cases (within 10-15% of threshold) are flagged for human review rather than auto-rejected.

### 4. Current Role Always Evaluated
The agent always fetches company intelligence for the candidate's current role, regardless of company type. An enterprise company employee might be doing startup-relevant IC work — skipping this data risks missing critical context.

## Example Outputs

### Qualified Candidate (Founding PM role)
- Tool calls: 4 (resume → company intel × 2 → recommendations)
- Result: Strong Fit with personalized outreach draft
- Agent reasoned: HireQuotient startup experience most relevant, fetched deep dive data

### Unqualified Candidate (Data Scientist role)
- Tool calls: 1 (resume only)
- Result: Not a Fit — domain mismatch
- Agent reasoned: PM career trajectory, no ML/data science background, fast rejected

## Cost Analysis

| Scenario | Tool Calls | Estimated Cost |
|----------|-----------|----------------|
| Full qualification (Strong/Potential Fit) | 4-6 | ~$0.006 |
| Fast reject (domain mismatch) | 1 | ~$0.001 |
| 1,000 candidates/day (40% mismatch) | Mixed | ~$38/day |
| Without fast reject guardrail | All full | ~$57/day |
| Monthly savings from fast reject | — | ~$564/month |

## Project Structure

```
├── agent.py              # Complete agent: tools, data, reasoning, runner
├── docs/
│   └── RESPONSIBLE_AI.md # Bias, privacy, guardrails, candidate rights framework
└── .env                  # API keys (not committed)
```

## How to Run

### Prerequisites
- Python 3.10+
- Anthropic API key

### Setup
```bash
git clone https://github.com/YOUR_USERNAME/ai-recruiter-agent.git
cd ai-recruiter-agent
python -m venv venv
source venv/bin/activate
pip install anthropic python-dotenv
cp .env.example .env
# Add your Anthropic API key to .env
```

### Run
```bash
python agent.py
```

1. Paste a job description, type `END`
2. Add vetting criteria with must-have/nice-to-have priority
3. Type `DONE` to run the agent
4. Watch the agent decide which tools to call in real time

## Responsible AI

This agent includes a comprehensive responsible AI framework covering:
- **Bias mitigation:** Company brand bias, tenure bias, education bias, recency bias
- **Inference guardrails:** All claims must trace to tool call data, no unsupported inferences
- **Privacy:** Only publicly available data, no storage beyond session, GDPR-aware
- **Human-in-the-loop:** Agent recommends, humans decide. No auto-rejection without review.
- **Candidate rights:** Transparency, dispute process, opt-out, human review option

See [docs/RESPONSIBLE_AI.md](docs/RESPONSIBLE_AI.md) for the full framework.

## Tech Stack

- **LLM:** Claude Haiku (claude-haiku-4-5-20251001) with native tool_use API
- **Architecture:** Custom agent loop with conditional tool calling — no LangChain agents
- **Data:** Mock company intelligence and Glassdoor data (swappable with real APIs)

## What I'd Build Next

1. **Real API integrations** — Replace mock data with LinkedIn API, Glassdoor API, Crunchbase for live company intelligence
2. **Multi-candidate comparison** — Accept multiple resumes, rank candidates against the same JD
3. **Recruiter feedback loop** — Track which qualifications recruiters agree/disagree with, use to improve prompts
4. **Model routing** — Use Haiku for fast rejects, escalate borderline candidates to Sonnet for deeper analysis
5. **Streamlit UI** — Visual interface with JD input, criteria builder, and report viewer
