# AI Collaboration Journal

**Project:** Employment Hero — Recruitment Management System (RMS) telemetry analysis  
**Candidate:** Juan José Manriquez  
**Role:** Intermediate Fullstack .NET Engineer  
**Consolidated on:** 19 October 2026  
**Approach:** Human-directed, AI-assisted development  
**Recorded AI interaction interface:** ChatGPT Desktop application  

---

## 1. Purpose and scope

This journal records how AI was used while developing a telemetry-analysis prototype for the RMS scenario. Its purpose is to make the human–AI interaction auditable: the questions raised by the developer, the assistance supplied by AI, the decisions retained by the human, and the validation or limitations applied to the results.

The prototype explores five scenario signals: `TECH_DEBT`, `SYSTEM_LAG`, `OPERATIONAL_OVERHEAD`, `LOW_ADOPTION`, and `FEATURE_PRESSURE`. The `system_signals.log` traces are **synthetic data** generated to test the analytical workflow. Therefore, the results describe the simulation's behaviour; they are not verified Employment Hero production measurements.

## 2. Human–AI collaboration summary

The developer defined the problem, scope, signals to observe, constraint of selecting no more than two initiatives, and quantitative methods to include. AI supported the conversion of those decisions into Python code, result analysis, explanation of statistical concepts, workflow troubleshooting, and technical communication.

The ChatGPT Desktop application was used as the conversational interface to:

- discuss analysis and design options;
- request and review implementation proposals;
- clarify Pearson correlation, *p*-values, and heatmaps;
- structure the report and this journal.

The use of ChatGPT does not replace technical review or transfer accountability for the outcome. Scope decisions, prioritisation criteria, and final approval remained the developer's responsibility.

## 3. Interaction log

| Stage | Human input | AI assistance | Outcome and human decision |
| --- | --- | --- | --- |
| Challenge understanding | Identified the constraints: $0 additional budget, no additional headcount, and capacity for only one or two initiatives. | Suggested translating the scenario into a telemetry prototype with quantitative evaluation. | The use of synthetic data was approved as analytical support, not production evidence. |
| Data generation | Defined the five signal categories and requested configurable scenarios. | Helped structure a JSON Lines generator with sessions, timestamps, severity, and event details. | `generate_logs.py` and `system_signals.log` were created. |
| Severity prioritisation | Requested totals, percentages, and severity weighting. | Proposed a frequency table and weighted score. | Category and severity breakdowns were reviewed; the score is a heuristic, not a measure of actual cost. |
| Correlation | Asked whether relationships between categories could reveal indirect effects when prioritising two initiatives. | Explained how to construct a session-level binary matrix, calculate Pearson correlation, and display heatmaps and *p*-values. | Correlation was included as an exploration of co-occurrence. It was documented that it does not prove causality. |
| Interpretation | Requested help understanding correlation and significance outputs. | Explained coefficients and visualisation. | Interpretation was limited to association within the simulation; no production causality was asserted. |
| Documentation | Requested a clearer AI journal including the code used. | Proposed a traceable structure containing methodology, code, tools, and limitations. | This journal consolidates the record and distinguishes facts, assumptions, and decisions. |

## 4. Decisions made by the human and work assisted by AI

### Human decisions

- Use a simulation because production telemetry is unavailable for the challenge.
- Select the five signal categories and evaluate priorities under limited capacity.
- Request frequency, severity distribution, weighted scoring, and session-level correlation.
- Require that results be presented with statistical and data limitations.
- Make the final recommendation after reviewing the results and business context.

### Activities assisted by AI

- Proposing Python data structures and functions.
- Organising synthetic-log generation, JSON Lines parsing, and visualisations.
- Explaining Pearson correlation, correlation matrices, *p*-values, and heatmaps.
- Suggesting table layouts and writing suitable for technical and executive audiences.
- Supporting the consistency review of the narrative and its limitations.

## 5. Tool architecture and usage

The following diagram shows the development-time architecture, the role of each tool, and the flow of data and review. It does not represent the runtime architecture of an Employment Hero production system.

```mermaid
flowchart TD
    H["Human developer<br/>Defines scope, hypotheses, priorities and validation"]
    C["ChatGPT Desktop<br/>Conversation, code assistance, explanation and report drafting"]
    V["Visual Studio Code<br/>Edits, runs and reviews Python source"]

    subgraph AI["Declared AI development toolchain"]
        OR["OmniRoute<br/>Model-routing layer"]
        N["Nemotron<br/>Reasoning/coding assistance"]
        GF["Gemini Flash Preview<br/>Reasoning/coding assistance"]
        LM["LM Studio<br/>Local model runtime"]
        GE["Gemma<br/>Locally available model"]
    end

    subgraph G["Synthetic telemetry generation"]
        PY1["Python standard library<br/>json, random, datetime, os"]
        NP1["NumPy<br/>Seeded numerical support"]
        GEN["generate_logs.py<br/>Configurable sessions and linked scenarios"]
        LOG["system_signals.log<br/>JSON Lines synthetic events"]
    end

    subgraph A["Analysis and visualisation"]
        PY2["Python standard library<br/>JSON file reading and paths"]
        PD["pandas<br/>DataFrames, crosstabs and summaries"]
        NP2["NumPy<br/>Matrix operations"]
        SC["SciPy / pearsonr<br/>Pearson r and p-values"]
        M["Matplotlib + Seaborn<br/>Charts and heatmaps"]
        AN["analyze.py<br/>Load, clean, score and correlate"]
        AUX["analyze_signals.py and<br/>analyze_signal_correlations.py<br/>Focused/earlier analysis scripts"]
        OUT["results/<br/>Tables, frequency charts, severity charts and correlation heatmaps"]
    end

    H -->|questions, acceptance criteria, review| C
    C -->|implementation options, explanations, draft text| H
    H -->|requirements and approved changes| V
    C -->|reviewed code suggestions| V
    V -->|routes eligible requests| OR
    OR --> N
    OR --> GF
    V -->|local inference when selected| LM
    LM --> GE
    V --> GEN
    PY1 --> GEN
    NP1 --> GEN
    GEN -->|writes| LOG
    LOG -->|reads| AN
    LOG -->|reads| AUX
    PY2 --> AN
    PD --> AN
    NP2 --> AN
    SC --> AN
    M --> AN
    AN -->|exports| OUT
    AUX -->|supports analysis/visualisation| OUT
    OUT -->|evidence for interpretation| H
```

| Tool or component | How it was used | Purpose |
| --- | --- | --- |
| ChatGPT Desktop | Conversational interface for AI-assisted development. | Explore implementation options, explain concepts, draft and improve documentation. |
| Visual Studio Code | Local development environment. | Edit, run, inspect, and review the Python scripts. |
| OmniRoute | Configured as a model-routing layer in the development workflow. | Direct eligible development-assistance requests to configured models. |
| Nemotron | Available through the configured OmniRoute workflow. | Provide reasoning and coding assistance when selected. |
| Gemini Flash Preview | Available through the configured OmniRoute workflow. | Provide reasoning and coding assistance when selected. |
| LM Studio | Local inference environment. | Run locally available models as part of the development toolchain. |
| Gemma | Locally available model through LM Studio. | Support local/private model-assisted development when selected. |
| Python | Language used by the generator and analysis scripts. | Provide a repeatable data-generation and analytics workflow. |
| `json`, `random`, `datetime`, `os` | Python standard-library modules. | Read/write JSON Lines, create reproducible scenarios, manage timestamps, and handle paths. |
| NumPy | Imported by generation and analysis code. | Provide seeded numerical support and matrix operations. |
| pandas | Used to build DataFrames, summaries, crosstabs, and session matrices. | Transform log events into tabular analytical inputs. |
| SciPy (`pearsonr`) | Used in correlation routines. | Calculate Pearson correlation coefficients and associated *p*-values. |
| Matplotlib and Seaborn | Used by the analysis scripts. | Export frequency charts, severity charts, and correlation heatmaps. |
| `generate_logs.py` | Configurable synthetic-event generator. | Create repeatable JSON Lines test data. |
| `analyze.py` | Consolidated analysis pipeline. | Load, clean, summarise, score, correlate, and export outputs. |
| Focused analysis scripts | `analyze_signals.py` and `analyze_signal_correlations.py`. | Produce focused/earlier versions of the severity and correlation analysis. |

The model-routing and local-inference components are development tools, not dependencies of the telemetry analyser at runtime. Their presence in the diagram does not imply that every request was sent to every model, or that every model was used for every task.

## 6. Technical structure analysed

The repository broadly separates data generation from analysis:

```text
generate_logs.py
  └─ CONFIG and generate_correlated_logs(...)
       └─ system_signals.log  (synthetic JSON Lines)

analyze.py
  ├─ load_logs(...) and preprocess_dataframe(...)
  ├─ build_session_matrix(...)
  ├─ calculate_correlations_with_pvalues(...)
  ├─ analyze_telemetry_signals(...)
  └─ tables and charts in results/

analyze_signals.py / analyze_signal_correlations.py
  └─ focused and earlier analysis scripts
```

### 6.1 Synthetic telemetry generation

`generate_logs.py` centralises the scenario in `CONFIG`: session count, simulated days, seed, and probabilities. Each exported line is a JSON object with `timestamp`, `session_id`, `signal_category`, `severity`, and `details`. This lets the analyser process the data without an additional rigid schema.

The relationship between selected events is deliberately implemented in the simulation. The following excerpt shows that `SYSTEM_LAG` can be generated after `TECH_DEBT`, and a support ticket can follow lag:

```python
has_tech_debt = random.random() < tech_debt_config["probability"]

if has_tech_debt:
    # records a TECH_DEBT event for the session
    has_system_lag = (
        random.random() < lag_config["probability_from_tech_debt"]
    )

    if has_system_lag:
        # records SYSTEM_LAG with the same session_id
        has_ticket = (
            random.random() < overhead_config["probability_from_lag"]
        )
```

This is useful for testing whether the pipeline can detect known co-occurrences. It also creates an important limitation: an observed correlation can reflect the rules used to create the simulation. It is not independent evidence that the same chain occurs in a real RMS.

### 6.2 Loading and normalisation

`analyze.py` is the main analysis path. `load_logs` reads each line as JSON and discards invalid entries; `preprocess_dataframe` validates required columns, normalises text, and extracts `eval_ms` when present in `details`.

```python
required_columns = ["session_id", "signal_category"]

df["session_id"] = df["session_id"].astype("string").str.strip()
df["signal_category"] = (
    df["signal_category"].astype("string").str.strip()
)
df["severity"] = (
    df["severity"].fillna("INFO").astype(str).str.strip().str.upper()
)
```

For a prototype, this prevents formatting differences and empty fields from silently changing counts. A production implementation should add a schema contract, data-quality metrics, and automated tests for malformed inputs.

### 6.3 Session matrix and correlation

Correlation is not calculated on isolated events. The code first builds a presence/absence matrix by session: each row is a session and each column a signal category; `1` means the category occurred at least once in that session.

```python
session_matrix = (
    pd.crosstab(df["session_id"], df["signal_category"]) > 0
).astype(int)

r, p_value = pearsonr(x, y)
```

`calculate_correlations_with_pvalues` then evaluates every column pair using `scipy.stats.pearsonr`. This answers the exploratory question, “Which signals tend to co-occur in the same sessions?” It is more accurate to call the result an association or co-occurrence than a causal relationship.

The correlation scripts produce an `r` matrix, a *p*-value matrix, and heatmaps using Seaborn and Matplotlib. *P*-values help assess compatibility with a null hypothesis in the simulated sample, but they do not remove simulation bias, omitted variables, or dependence between observations.

### 6.4 Frequency, severity, and weighted risk

`analyze_signals.py` summarises volume by category and cross-tabulates category against severity. Its focused version uses the weights `ERROR = 10`, `WARN = 3`, and `INFO = 1`:

```python
severity_weights = {"ERROR": 10, "WARN": 3, "INFO": 1}
df["risk_weight"] = df["severity"].map(severity_weights).fillna(1)
risk_scores = df.groupby("signal_category")["risk_weight"].sum()
```

The score supports a capacity-constrained discussion because it combines frequency and exercise-defined severity. It should be presented as a prioritisation heuristic; it does not estimate financial cost, implementation effort, or actual causal impact.

## 7. Results the prototype can communicate

The workflow can produce:

- event count and percentage by category;
- `ERROR`, `WARN`, and `INFO` breakdowns;
- weighted risk score;
- session-level Pearson correlation matrix;
- *p*-value matrix;
- frequency and severity charts and correlation heatmaps.

These outputs provide a reproducible basis for prioritisation hypotheses. For example, if `TECH_DEBT` and `SYSTEM_LAG` frequently co-occur in the simulated data, that justifies investigating whether simplifying customised rules and improving search/bulk-action paths are high-value initiatives. It does not establish that fixing one will automatically remove the other, nor that support tickets will be resolved without production validation.

## 8. Limitations and quality controls

1. **Synthetic data.** Generator rules affect the observed correlations and counts.
2. **Correlation is not causation.** Pearson quantifies linear association; it does not identify direction, mechanism, or root cause.
3. **Session-level binary matrix.** The analysis measures within-session co-occurrence, not temporal sequence, duration, latency, or temporal causality.
4. **Heuristic weights.** Severity weights should be agreed with business and operations stakeholders before production use.
5. **Validation required.** A production recommendation would require representative telemetry, segmentation by customer and endpoint, tracing, performance tests, and engineering review.
6. **Code review.** The repository contains overlapping scripts (`analyze.py`, `analyze_signals.py`, and `analyze_signal_correlations.py`). A production version should retain one entry point, tests, and external configuration.

## 9. Responsible next steps

1. Confirm the simulation hypotheses with production telemetry.
2. Define success measures for each initiative: search p95/p99, bulk-action failures, support-ticket volume, and feedback adoption.
3. Run a small, reversible intervention; measure before and after; and segment results.
4. Preserve configuration, code version, simulation parameters, and execution date for every run.
5. Keep human review of AI-generated recommendations and final conclusions.

## 10. Conclusion

AI accelerated implementation, statistical exploration, and technical communication. The developer retained ownership of the problem, the analytical choices, the assessment of limitations, and the final decision. The result is a reproducible telemetry-analysis prototype that can formulate and prioritise hypotheses, while avoiding the mistake of treating synthetic data or statistical correlation as causal production evidence.
