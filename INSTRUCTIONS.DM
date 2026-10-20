Hi Juan Jose Manriquez,

Thank you for your interest in the Intermediate Fullstack .NET Engineer - Remote role at Employment Hero.

We're excited to invite you to the next stage of our hiring process. As part of this stage, you'll be asked to complete the following assessments.

Step 1. AI-Native Engineering Challenge

A practical, real-world engineering challenge designed to help us understand how you approach problems and collaborate with AI.

Team SituationTeam Situation
You are a Software Engineer in a team responsible for a Recruitment Management System (RMS). The product helps recruiters, hiring managers, and interviewers manage candidates throughout the hiring process, from application to offer.   
Recently, several signals have started to emerge:   
System Lag: Candidate search and candidate status updates (qualified / disqualified) can take several seconds to complete. Customers have started complaining about performance issues when performing bulk actions.   
Tech Debt: The codebase has become increasingly difficult to maintain and extend because the team has hard-coded too many customer-specific hiring workflows and approval rules for enterprise customers.   
Low Adoption: A recently released candidate feedback feature has a much lower adoption rate than expected. Many hiring managers still prefer using spreadsheets and Slack to share candidate feedback.   
Operational Overhead: Support tickets related to candidate search, status updates, and bulk actions have increased by 30%.   
Feature Pressure: Several large enterprise customers have requested automated CV screening and interview scheduling capabilities before committing to renew or expand their contracts.   
 
 Constraints 
 Your Task & SubmissionConstraints
 No additional budget is available.   
 No additional headcount is available.   
 Given current capacity, the team can realistically invest in only one or two major initiatives next month.   Your Task
As a Software Engineer in the team, analyse the situation, decide what you would prioritise and why, and explain how AI influenced your thinking and recommendations. 

  Submission
Submit the following files through the Google Form linked in your invitation email:   Recommendation   AI Collaboration Journal   There is no required format or length.   Use any format you think best communicates your thinking.   Use any AI tools you find helpful.   

# 🛠️ AI-Native Tooling, Infrastructure & Setup Strategy

Due to the strict budget constraints (**$0 USD additional budget available**), a hybrid AI infrastructure was engineered locally using cost-efficient and free open-weight LLMs, ensuring high-throughput reasoning without cloud API overhead.

---

## 🏗️ Architecture & Local AI Ecosystem

* **IDE & Workflow Interface:** VS Code (integrated via OpenCode / custom routing extension).
* **AI Orchestration & Routing:** **OmniRoute** acting as the central model router:
  * Primary Reasoning Models: `Nemotron` & `Gemini 2.5/3 Flash Preview` (Free Tier APIs).
* **Local Inference Engine:** **LM Studio** serving quantized local models:
  * Backup & Data Privacy Model: `Gemma` (running completely offline on local hardware).

---

##  Roadmap & Execution Plan

###  Phase 1: Telemetry Data Generation & Quantitative Analysis
* [ ] **Task 1.1 — Synthetic Log Generation:** Use a python script to enerate a consolidated `system_signals.log` file quantitatively simulating telemetry metrics, error traces, and user events for the 5 key signals (System Lag, Tech Debt, Low Adoption, Operational Overhead, Feature Pressure)[cite: 1].
* [ ] **Task 1.2 — Signal Analysis Script:** Develop a Python processing script to parse, filter, and categorize signals directly from `system_signals.log`.
* [ ] **Task 1.3 — Telemetry Visualization:** Produce a sorted bar chart (Python/Matplotlib) illustrating incident frequency and system severity from highest to lowest impact.

###  Phase 2: Architecture & Infrastructure Documentation
* [ ] **Task 2.1 — Architecture & Tooling Write-up:** Document the technical architecture, local LLM setup, routing strategies (OmniRoute + LM Studio), and software design patterns used to address tech debt.

###  Phase 3: Strategic Assessment & Recommendations
* [ ] **Task 3.1 — Recommendation Document (`Recommendation.pdf` / `.md`):** Draft the executive summary and 1-to-5 prioritized roadmap, establishing the capacity line at Rank 2 based on team capacity constraints.

###  Phase 4: Auditability & AI Transparency
* [ ] **Task 4.1 — AI Collaboration Journal (`AI_Collaboration_Journal.md`):** Complete the interaction log detailing user prompts, LLM recommendations, human overrides, and architectural refinements[cite: 2].