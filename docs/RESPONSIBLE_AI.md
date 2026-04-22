# Responsible AI Framework: AI Recruiter Agent

**Author:** Vishal Goyal  
**Date:** April 2026  
**Applies to:** ai-recruiter-agent

---

## 1. Purpose

This document outlines the risks, mitigations, and policies for using an AI agent to qualify job candidates. Automated candidate evaluation carries significant responsibility — wrong decisions affect real people's livelihoods and careers.

---

## 2. Risk Categories

### 2.1 Bias and Fairness

**Risk: Company brand bias**  
The agent uses company intelligence (stage, funding, Glassdoor rating) as qualification signals. This can create implicit bias: candidates from well-known companies (Google, Meta) get boosted, while candidates from unknown startups get penalized — regardless of individual performance.

**Mitigation:**  
- Company intelligence informs context, never directly determines fit score
- Agent must cite candidate-specific achievements, not company reputation, as evidence
- System prompt explicitly states: "Evaluate the candidate's individual contributions, not the prestige of their employer"

**Risk: Tenure bias**  
Short tenure at a company can be flagged negatively ("couldn't last") without understanding context. The same company might have systemic issues (high turnover, toxic culture) that explain short stays.

**Mitigation:**  
- Compare candidate tenure against company baseline (average tenure of similar roles at that company during overlapping period)
- If company has high overall turnover, normalize the candidate's tenure against that baseline
- Flag tenure as neutral when insufficient comparison data exists, rather than assuming negative

**Risk: Education bias**  
The agent sees "BCA" vs "B.Tech" vs "MBA" and may weight prestigious degrees higher without evidence they predict job performance.

**Mitigation:**  
- Education is treated as a checkbox (meets minimum requirement or not), never as a ranking signal
- No inference about candidate quality based on institution name unless the JD explicitly requires specific credentials

**Risk: Recency bias**  
The agent weighs recent roles more heavily. A candidate who had a strong early career but a weaker recent role may be unfairly penalized, while a candidate with a recent impressive title at a weak company may be unfairly boosted.

**Mitigation:**  
- Evaluate achievements with specific metrics across all relevant roles, not just the most recent
- System prompt instructs: "Assess trajectory and pattern of impact, not just current title"

### 2.2 Inference and Hallucination

**Risk: Unsupported inferences**  
The agent may infer facts not present in the data. Example: "ServiceNow requires 5+ years for direct hire" was stated in our mock data, but in production, such claims might be assumptions the agent generates on its own.

**Mitigation:**  
- Every factual claim in the report must be traceable to a specific tool call result
- System prompt includes: "Do not infer qualifications, compensation, or role requirements that are not explicitly stated in the data. If you are uncertain, say so."
- Guardrail: if the agent makes a claim about a company's hiring bar, it must have come from the company intelligence tool, not generated from training data

**Risk: Over-inference from recommendations**  
LinkedIn recommendations are inherently positive (people don't publish negative ones). The agent should not treat absence of recommendations as a negative signal, nor treat their presence as proof of exceptional performance.

**Mitigation:**  
- Recommendations validate claims, they don't replace evidence
- Absence of recommendations is reported as "no data available," not as a gap
- System prompt: "Recommendations are supplementary evidence. They confirm but do not replace quantified achievements."

### 2.3 Privacy and Data Use

**Risk: Using data candidates didn't consent to**  
The agent uses Glassdoor ratings, LinkedIn recommendations, and social proof. While this information is publicly available, candidates may not expect it to be used in automated hiring decisions.

**Mitigation:**  
- Disclose to hiring companies which data sources are used in qualification
- Do not use private or scraped data — only publicly available information
- Provide candidates with the ability to see what data was used and dispute inaccuracies if they request it (GDPR compliance)
- Never store or process protected characteristics (age, gender, ethnicity, disability status)

**Risk: Data retention**  
Candidate data processed by the agent could be retained and used inappropriately.

**Mitigation:**  
- No candidate data is stored beyond the session unless explicitly opted in
- Tool call results are not logged to external services
- API calls to Claude do not retain conversation data (per Anthropic's API data policy)

### 2.4 Outreach and Candidate Experience

**Risk: Misleading outreach**  
If the qualification is wrong but the agent drafts outreach anyway, the candidate receives a message based on incorrect analysis. This wastes their time and damages the hiring company's brand.

**Mitigation:**  
- Outreach is only drafted for "Strong Fit" or "Potential Fit" scores
- The outreach draft is a suggestion for human review, never auto-sent
- All outreach includes specific achievements from the resume so the candidate can verify relevance
- Guardrail: if any must-have vetting criterion is "Not Met," outreach is blocked regardless of overall score

**Risk: Generic or tone-deaf outreach**  
Mass-generated outreach that feels robotic or makes incorrect assumptions about the candidate's interests damages employer brand.

**Mitigation:**  
- Outreach must reference at least 2 specific, verifiable achievements from the candidate's background
- Outreach must connect the candidate's experience to the specific JD, not use generic templates
- Human recruiter reviews and personalizes before sending

---

## 3. Human-in-the-Loop Requirements

This agent is a **decision support tool**, not a decision maker.

| Action | Automation level | Human required? |
|--------|-----------------|-----------------|
| Resume parsing | Fully automated | No |
| Company intelligence lookup | Fully automated | No |
| Qualification scoring | Automated with reasoning | Human reviews before acting |
| Reject decision | Automated recommendation | Human confirms before rejecting |
| Outreach drafting | Automated draft | Human reviews and sends |
| Final hire/no-hire | Never automated | Always human decision |

**Key principle:** The agent recommends, humans decide. No candidate is auto-rejected or auto-advanced without human review.

---

## 4. Monitoring and Evaluation

### Quality metrics to track
- Qualification accuracy vs human recruiter decisions (agreement rate)
- False rejection rate (qualified candidates incorrectly rejected)
- False advancement rate (unqualified candidates incorrectly advanced)
- Bias audit: qualification rates segmented by company tier, education level, career gap presence

### Bias audits (quarterly)
- Compare qualification rates across candidate demographics (where legally permissible to measure)
- Check if company brand correlates with scores independent of individual achievements
- Verify that tenure-based assessments use company baseline normalization
- Review fast-reject guardrail for false positive rate

### Cost tracking
- Cost per qualification by outcome type (fast reject vs full analysis)
- Model usage distribution (Haiku vs Sonnet escalation rate)
- Token efficiency trends over time

---

## 5. Candidate Rights

1. **Transparency:** Candidates can request to know what data sources were used in their evaluation
2. **Dispute:** Candidates can challenge factual inaccuracies in the qualification report
3. **Opt-out:** Candidates can request their data not be processed by the AI agent
4. **Human review:** Any candidate can request a human-only evaluation instead of AI-assisted evaluation
5. **No auto-rejection:** No candidate is permanently rejected based solely on AI assessment without human review

---

## 6. Red Lines (Never Do)

1. Never use age, gender, ethnicity, nationality, disability, or any protected characteristic in qualification
2. Never auto-send outreach without human review
3. Never make a final hire/reject decision without human confirmation
4. Never infer protected characteristics from names, locations, or education institutions
5. Never penalize career gaps without understanding context
6. Never use compensation data or salary history in qualification (illegal in many jurisdictions)
7. Never store candidate data beyond the active evaluation session without consent
