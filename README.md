
# AI Portfolio Intelligence Assistant

An evidence-grounded AI application that transforms weekly portfolio reporting data into executive-level insights.

## Overview


Enterprise leaders often manage complex portfolios spanning multiple teams, competing priorities, delivery risks, and interdependent initiatives. Traditional status reporting can make it difficult to distinguish routine progress updates from issues requiring leadership attention.

The AI Portfolio Intelligence Assistant is a working proof of concept that transforms structured portfolio reporting data into actionable executive intelligence. It combines deterministic change detection with generative AI to identify delivery deterioration, milestone movement, cross-team dependencies, and decisions requiring intervention.

The project demonstrates an evidence-first approach to AI-assisted portfolio governance: using automation to reduce manual analysis, surface meaningful changes, and support more informed leadership discussions while retaining human oversight.


The application:

- Ingests structured portfolio data from Excel workbooks.
- Compares weekly portfolio snapshots to identify material changes.
- Detects status deterioration, milestone delays, emerging risks, blockers, and dependencies.
- Uses the OpenAI API to synthesize findings into a concise executive brief.
- Evaluates selected AI-generated claims against structured evidence.



## Example: Executive Portfolio Intelligence

**[View the complete AI-generated executive brief](examples/sample_executive_brief.md)**

The following example illustrates how the application analyzes two weekly snapshots of a synthetic Digital Payments Modernization portfolio.

**Portfolio:** 8 initiatives

**Reporting period:** September 18–25, 2026

### Executive Snapshot

| Indicator | Finding |
|---|---|
| Delivery health | 3 initiatives deteriorated; 1 improved |
| Milestone movement | PAY-02 delayed by 21 days |
| Critical blocker | PAY-06 migration rehearsal blocked by incomplete data mapping |
| Emerging delivery risk | PAY-05 progressed from 45% to 65% completion but retains a high-severity reconciliation risk |
| Cross-team dependencies | PAY-03 exposed to PAY-02 delay; PAY-08 exposed to PAY-06 deterioration |
| Leadership decision | PAY-04 authentication architecture selection due October 2, 2026 |
| Stable/on track | PAY-01 |

### Leadership Attention

**1. Legacy Platform Migration (PAY-06)**

Delivery status deteriorated from amber to red. Incomplete legacy data mapping is preventing migration rehearsal from starting. The associated risk increased from medium to high.

**2. Real-Time Payments Rollout (PAY-02)**

Delivery status deteriorated from green to amber, with a 21-day milestone delay. Vendor certification delays reduce the time available for downstream integration and launch readiness.

**3. Payment Authentication (PAY-04)**

A decision is required on the target authentication architecture by October 2, 2026. Delaying the decision threatens the planned architecture and implementation schedule.

### Why This Matters

The demonstration illustrates how structured portfolio evidence can be transformed into an executive briefing that distinguishes:

- Delivery progress from actual delivery health.
- Individual initiative issues from cross-team dependency exposure.
- Status reporting from decisions requiring leadership attention.

The application calculates portfolio changes deterministically, uses generative AI to synthesize the narrative, and applies targeted automated checks to selected claims.

All findings are based on fictional demonstration data.


## Demonstration Data

The project uses a fully synthetic **Digital Payments Modernization** portfolio consisting of eight initiatives (PAY-01 through PAY-08).

Two weekly snapshots represent September 18 and September 25, 2026.

All initiative details, risks, dependencies, and decisions are fictional and intended solely for demonstration.

## Design Principles

1. **Evidence before synthesis:** Portfolio changes are calculated programmatically before being provided to the AI model.
2. **Separation of responsibilities:** Python handles deterministic comparisons; generative AI handles executive narrative synthesis.
3. **Traceability:** Structured comparison results provide the evidence supporting executive summaries.
4. **Automated validation:** Targeted checks flag unsupported identifiers and incorrect milestone-delay claims.
5. **Explicit limitations:** Passing automated checks does not guarantee that every AI-generated statement is accurate.


## Architecture

The application follows a five-stage pipeline:

```text
Weekly Excel Workbooks
         |
         v
1. Excel Ingestion & Validation
   ingest_portfolio.py
         |
         v
2. Portfolio Change Detection
   compare_portfolio.py
         |
         v
3. AI Executive Synthesis
   synthesize_brief.py
         |
         v
4. Evidence-Based Evaluation
   evaluate_brief.py
         |
         v
5. Executive Brief + Evaluation Result
```

### Key Components

| File | Responsibility |
|---|---|
| `run_pipeline.py` | Orchestrates the end-to-end workflow |
| `ingest_portfolio.py` | Validates Excel workbooks and produces structured JSON |
| `compare_portfolio.py` | Calculates portfolio changes between weekly snapshots |
| `synthesize_brief.py` | Uses the OpenAI API to generate an executive brief |
| `evaluate_brief.py` | Checks selected AI-generated claims against structured evidence |
| `build_templates.py` | Supports generation of demonstration workbook templates |
| `tests/` | Contains automated ingestion, comparison, and evaluation tests |

## Running the Application

### Prerequisites

- Python 3
- OpenAI API access
- Python packages: `openai` and `openpyxl`


### Installation

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project's pinned dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Configure your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

Never commit actual API keys or credential files to Git.

### Execute the Pipeline

From the project directory:

```bash
python3 run_pipeline.py
```

The pipeline processes both weekly Excel workbooks, compares portfolio changes, generates an AI executive brief, and evaluates selected claims.

### Generated Outputs

| File | Description |
|---|---|
| `portfolio_week_1.json` | Validated Week 1 portfolio snapshot |
| `portfolio_week_2.json` | Validated Week 2 portfolio snapshot |
| `portfolio_changes.json` | Structured comparison evidence |
| `brief_v2.txt` | AI-generated executive brief |

The pipeline reports whether its configured evidence checks passed or failed.


## Automated Testing

The project includes 13 automated tests using Python's built-in `unittest` framework.

Run the tests from the project directory:

```bash
python3 -m unittest discover -s tests -v
```

### Test Coverage

| Category | Tests | Coverage |
|---|---:|---|
| Excel ingestion | 3 | Missing required columns, duplicate initiative IDs, invalid dependencies |
| Portfolio comparison | 3 | Known portfolio changes, status deterioration, progress versus delivery health |
| Executive brief evaluation | 7 | Critical evidence presence, identifier validation, milestone-delay verification, and negative tests |
| **Total** | **13** | |

The automated tests do not require OpenAI API calls. They use existing portfolio data, comparison evidence, and a previously generated executive brief.

### Validation Approach

The application separates deterministic calculations from AI-generated narrative.

The evaluation module checks selected claims, including:

- Whether referenced initiative IDs exist in the portfolio.
- Whether referenced risk and blocker IDs appear in the supported evidence.
- Whether explicitly reported milestone delays agree with calculated values.

Negative tests demonstrate that the evaluator can identify deliberately introduced errors, including an invented initiative and an incorrect milestone delay.

## Limitations

This project is a working demonstration, not a production-ready enterprise reporting platform.

Current limitations include:

- The evaluator does not verify every factual claim in the generated brief.
- Decision deadlines, risk severity descriptions, and causal statements are not comprehensively validated.
- The pipeline uses two predefined weekly snapshots rather than a continuously updated data source.
- The application does not provide a graphical user interface.
- AI-generated summaries require human review before use in consequential decisions.

## Project Status

The following capabilities have been implemented and tested:

- Excel ingestion and validation
- Week-over-week portfolio comparison
- AI-generated executive briefing
- Automated evidence evaluation
- End-to-end pipeline execution
- 13 passing automated tests

Potential future enhancements include broader claim validation, additional reporting periods, structured evaluation reports, and an interactive dashboard.

## Disclaimer

All portfolio data is synthetic. This project does not contain or represent confidential information from any employer or client.