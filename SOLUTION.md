# MFGX AI --- Solution

## 1. Problem Statement

Modern manufacturing environments generate large amounts of operational
data from production lines, machines, quality inspections, downtime
events, maintenance records, and Standard Operating Procedures (SOPs).

When a production problem occurs, a supervisor or production engineer
may need to manually search several sources to understand what happened,
why it happened, whether the problem has occurred before, and what
action should be taken.

The problem addressed by MFGX AI is:

> How can factory operational data and SOP documents be combined into an
> AI-powered system that lets a user ask a natural-language
> investigation question and receive a concise, evidence-grounded
> explanation and recommended action?

The system must also avoid inventing information when the required data
is unavailable and must keep different investigation questions focused
on their actual intent.

------------------------------------------------------------------------

## 2. Solution

**MFGX AI (Manufacturing Factory Investigation AI)** is a Production
Investigation Copilot.

A user can ask a question such as:

> "Why did Line L3 miss its production target on August 4, and what
> action should be taken?"

MFGX AI understands the question, identifies the relevant
line/machine/date and investigation intent, retrieves the relevant
factory evidence and SOP information, and produces a focused
investigation result.

It supports:

-   Production target investigations
-   Machine downtime investigations
-   Recurring maintenance investigations
-   Quality and rejection investigations
-   Supervisor-action questions
-   Financial/operator data-availability questions
-   Out-of-scope question handling

------------------------------------------------------------------------

## 3. Simple Explanation

MFGX AI works like a digital investigator for a factory.

### Without MFGX AI

A supervisor may have to:

1.  Find the production record.
2.  Check target and actual production.
3.  Search downtime records.
4.  Check maintenance history.
5.  Review quality records.
6.  Find the correct SOP.
7.  Compare the evidence.
8.  Determine the likely cause.
9.  Decide what action should be taken.

### With MFGX AI

The supervisor can ask one natural-language question.

The system:

1.  Understands the question.
2.  Detects its intent and important entities.
3.  Retrieves relevant factory data.
4.  Retrieves relevant SOP evidence.
5.  Connects the evidence.
6.  Generates a focused answer.
7.  Recommends an SOP-grounded action.

------------------------------------------------------------------------

## 4. How the System Works

``` text
User Question
     |
     v
Query Understanding
     |
     v
Intent & Entity Detection
     |
     v
Relevant Factory Data
     |
     v
SOP Retrieval (RAG)
     |
     v
Evidence Grounding
     |
     v
Investigation Synthesis
     |
     v
Answer + Evidence + Recommended Action
```

### Step 1 --- User Question

The user enters a natural-language question.

Example:

> "What happened to machine M301 on August 4?"

No database query or technical command is required.

### Step 2 --- Query Understanding

The system extracts entities such as:

-   Production line: L1--L4
-   Machine: M101--M404
-   Date: YYYY-MM-DD

It also classifies the investigation intent.

Supported intents include:

1.  `PRODUCTION_TARGET`
2.  `QUALITY_DEFECT`
3.  `DOWNTIME_EVENT`
4.  `MAINTENANCE_RECURRING`
5.  `SUPERVISOR_ACTION`
6.  `FINANCIAL_UNAVAILABLE`
7.  `OPERATOR_UNAVAILABLE`
8.  `UNSUPPORTED_OUT_OF_SCOPE`

### Step 3 --- Intent-Aware Investigation

Different questions use different evidence.

For example:

-   Production question → production target, actual production,
    shortfall, downtime, recovery guidance
-   Quality question → rejected units, rejection rate, defect
    information, quality SOPs
-   Maintenance question → maintenance history, recurring warnings,
    cooling-system evidence
-   Supervisor question → operational response procedures and relevant
    SOPs

This prevents every question from producing the same generic answer.

### Step 4 --- Factory Data Investigation

The system uses available factory datasets such as:

-   Production records
-   Downtime records
-   Quality records
-   Maintenance records

For the main Line L3 investigation, the verified evidence includes:

-   Production target: **3,300**
-   Actual production: **2,895**
-   Shortfall: **405 units**
-   Shortfall rate: **12.27%**
-   M301 overheating downtime: **47 minutes**
-   Quality rejections: **139 units**
-   Quality rejection rate: **4.80%**
-   Four historical maintenance records for M301

### Step 5 --- SOP Retrieval

MFGX AI uses Retrieval-Augmented Generation (RAG) to retrieve relevant
SOP sections.

The project uses SOP documents including:

-   `SOP-301` --- Cooling System Inspection
-   `SOP-302` --- M301 Overheating Response
-   `SOP-304` --- Quality Inspection / relevant operational procedures
-   `SOP-305` --- Target Recovery

The retrieved SOP evidence is used to ground recommended actions.

------------------------------------------------------------------------

## 5. Lightweight RAG Architecture

The original RAG implementation used PyTorch, SentenceTransformers, and
ChromaDB. These components created a large memory footprint and caused
problems with the Render Free 512 MB memory limit.

The production retrieval layer was redesigned as a lightweight hybrid
system.

### Mode A --- Cloud Embeddings

When a suitable API key is available, cloud embeddings are used for
dense vector retrieval. NumPy is used to calculate similarity against
precomputed SOP embeddings.

### Mode B --- TF-IDF Fallback

If cloud embedding access is unavailable, rate-limited, times out, or
fails, the system falls back to local TF-IDF retrieval.

The fallback uses:

``` text
TfidfVectorizer(
    ngram_range=(1, 3),
    sublinear_tf=True
)
```

This removes the need to load PyTorch and ChromaDB in the production
runtime.

### Why this matters

The reported validation measured approximately:

-   Application after initialization: **128.90 MB**
-   After first investigation: **129.85 MB**
-   After 30+ investigations: **129.93 MB**
-   Concurrent-request measurement: **130.23 MB**
-   Reported peak during testing: approximately **157.41 MB**

The 55-request stress test reported only about **0.35 MB** memory drift.

This makes the backend much more suitable for a low-memory cloud
environment.

------------------------------------------------------------------------

## 6. Evidence-Grounded Answers

The system separates available evidence from unavailable information.

For example, if the user asks:

> "What was the exact financial cost of the M301 failure?"

MFGX AI does not invent a number. It states that financial cost records
are not present in the available factory dataset and points the user
toward appropriate external financial/ERP records.

Similarly, if the user asks:

> "Which operator was responsible for M301?"

The system explains that operator names and individual personnel
assignments are not available in the factory dataset.

This reduces unsupported claims and improves trustworthiness.

------------------------------------------------------------------------

## 7. Out-of-Scope Handling

MFGX AI is designed for factory production investigations involving:

-   Production
-   Downtime
-   Maintenance
-   Quality
-   SOP-related operational issues

If a user asks an unrelated question such as:

> "What is the weather today?"

the system does not pretend that it is a factory investigation system.
It provides scope guidance and suggests supported investigation
scenarios.

------------------------------------------------------------------------

## 8. Example Investigation

Question:

> "Why did Line L3 miss its production target on August 4, and what
> action should be taken?"

Verified evidence:

``` text
Target Production   = 3,300
Actual Production   = 2,895
Shortfall           = 405 units
Shortfall Rate      = 12.27%
M301 Downtime       = 47 minutes
Quality Rejections  = 139 units
Rejection Rate      = 4.80%
```

MFGX AI connects this evidence with relevant SOP guidance and explains
the likely contributing factors and appropriate supervisor action.

The important principle is that the result is grounded in the available
factory evidence rather than unsupported assumptions.

------------------------------------------------------------------------

## 9. Example Intent-Aware Questions

### Production

> Why did Line L3 miss its production target?

Focus: target, actual production, shortfall, downtime, and recovery.

### Machine Downtime

> What happened to machine M301 on August 4?

Focus: 47 minutes of overheating-related downtime and machine response.

### Maintenance

> Investigate the recurring temperature problems on M301.

Focus: recurring temperature warnings, cooling abnormalities, and four
historical maintenance records.

### Quality

> Why did Line L3 have a high rejection rate on August 4?

Focus: 139 rejected units and the 4.80% rejection rate.

### Financial

> What was the exact financial cost of the M301 failure?

Focus: clearly report that financial cost data is unavailable instead of
fabricating a value.

------------------------------------------------------------------------

## 10. System Architecture

``` text
                 USER
                   |
                   v
            Netlify Frontend
                   |
                   | HTTPS API
                   v
             FastAPI Backend
                   |
          +--------+--------+
          |                 |
          v                 v
   Factory Data         SOP Retrieval
          |                 |
          |          +------+------+
          |          |             |
          |      Cloud Embed    TF-IDF
          |          |          Fallback
          +----------+-------------+
                     |
                     v
             Investigation Engine
                     |
                     v
          Evidence + Recommendation
                     |
                     v
                 Frontend
```

------------------------------------------------------------------------

## 11. Main Benefits

### Faster Investigation

Users ask one natural-language question instead of manually searching
multiple records.

### Evidence Grounding

Results are based on available factory data and retrieved SOP evidence.

### Intent Awareness

Different questions receive different investigation paths and relevant
evidence.

### Reduced Hallucination Risk

Unavailable information is explicitly reported instead of being
invented.

### SOP-Based Recommendations

Recommended actions are connected to relevant operating procedures.

### Low-Memory Deployment

The lightweight RAG architecture removes heavy PyTorch and ChromaDB
production dependencies.

### Simple User Experience

The user only needs to describe the production problem in natural
language.

------------------------------------------------------------------------

## 12. Technology Overview

### Frontend

The frontend provides:

-   Investigation input
-   Investigation results
-   Supporting evidence
-   Production and quality information
-   Recommended actions
-   Scope guidance
-   Investigation report generation

### Backend

The backend provides:

-   FastAPI API
-   Factory data processing
-   Query intent detection
-   Entity extraction
-   Investigation logic
-   SOP retrieval
-   Evidence synthesis
-   Missing-data handling

### Retrieval Layer

The optimized retrieval layer uses:

-   Cloud embeddings when available
-   NumPy cosine similarity
-   Scikit-learn TF-IDF fallback
-   Precomputed SOP caches

------------------------------------------------------------------------

## 13. Testing and Validation

The project was validated through functional, regression, stress, and
live frontend testing.

### Main verified investigation values

-   Target: **3,300**
-   Actual: **2,895**
-   Shortfall: **405**
-   Shortfall rate: **12.27%**
-   M301 overheating downtime: **47 minutes**
-   Quality rejections: **139**
-   Rejection rate: **4.80%**
-   Historical M301 maintenance records: **4**

### Stress Testing

The reported stress test executed **55 investigation requests**,
including sequential and concurrent requests.

The optimized backend remained within the measured memory range and
showed approximately **0.35 MB** memory drift across the test.

### Frontend Build

The frontend build completed successfully using:

``` text
npm run build
```

The live Netlify application was also tested with multiple materially
different investigation questions.

------------------------------------------------------------------------

## 14. Project Outcome

MFGX AI turns a manual factory investigation process into a guided
AI-assisted workflow.

Instead of searching through production records, downtime logs,
maintenance history, quality data, and SOP documents separately, a user
can ask one question and receive:

-   A focused investigation
-   Relevant evidence
-   Supporting metrics
-   SOP-grounded recommendations
-   Clear handling of unavailable information

The core concept is:

``` text
Natural Language
       +
Factory Operational Data
       +
SOP Retrieval
       +
Intent-Aware Investigation
       +
Evidence Grounding
       =
MFGX AI
```

------------------------------------------------------------------------

## 15. Final Summary

### Problem

Factory investigations require users to manually combine production,
downtime, quality, maintenance, and SOP information.

### Solution

MFGX AI provides a natural-language investigation interface that
identifies the user's intent, retrieves relevant factory evidence and
SOP information, and produces a focused investigation result with
supporting evidence and recommended action.

### Key Innovation

The project combines **intent-aware investigation routing** with
**evidence-grounded SOP retrieval** and a **lightweight hybrid RAG
architecture** suitable for low-memory cloud deployment.

### Final Result

MFGX AI transforms:

> **"Search multiple factory records and SOPs manually"**

into:

> **"Ask one question and receive an evidence-grounded investigation."**

------------------------------------------------------------------------

## Project Status

**MFGX AI v0.1.0 MVP**

-   Core functionality: Complete
-   Intent-aware routing: Complete
-   Lightweight RAG: Complete
-   Regression testing: Passed
-   Memory stress testing: Passed
-   Frontend build: Passed
-   Live frontend testing: Passed
-   Deployment: Operational
