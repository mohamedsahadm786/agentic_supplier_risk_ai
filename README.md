# 🏭 Agentic Supplier Risk Intelligence System

> **A production-grade, multi-agent AI SaaS platform that automates international supplier risk assessment — replacing a 2–3 day manual compliance process with a ~10-minute AI-driven evaluation pipeline.**

<div align="center">

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Visit_App-blue?style=for-the-badge)](http://agentic-supplier-risk-frontend-786.s3-website.ap-south-1.amazonaws.com/platform-admin)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/mohamedsahadm786/agentic_supplier_risk_ai)
[![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![AWS](https://img.shields.io/badge/AWS-Deployed-FF9900?style=for-the-badge&logo=amazonaws)](https://aws.amazon.com)

</div>

---

## 📑 Table of Contents

1. [Project Overview](#1-project-overview)
2. [The Business Problem](#2-the-business-problem)
3. [Real-World Usage Scenario](#3-real-world-usage-scenario)
4. [System Architecture](#4-system-architecture)
   - [High-Level Architecture](#41-high-level-architecture)
   - [Low-Level Component Architecture](#42-low-level-component-architecture)
   - [Database Architecture & Connections](#43-database-architecture--connections)
   - [Container Network Architecture](#44-container-network-architecture)
5. [The 5-Agent Agentic Workflow](#5-the-5-agent-agentic-workflow)
   - [Workflow Orchestration Diagram](#51-workflow-orchestration-diagram)
   - [Agent 1 — Planner Agent](#52-agent-1--planner-agent)
   - [Agent 2 — Document Intelligence Agent](#53-agent-2--document-intelligence-agent)
   - [Agent 3 — RAG Knowledge Agent](#54-agent-3--rag-knowledge-agent)
   - [Agent 4 — External Intelligence Agent](#55-agent-4--external-intelligence-agent)
   - [Agent 5 — Decision & Report Agent](#56-agent-5--decision--report-agent)
6. [MCP Tool Groups](#6-mcp-tool-groups)
7. [RAG System](#7-rag-system)
8. [Tech Stack](#8-tech-stack)
9. [Database Schema](#9-database-schema)
10. [API Reference](#10-api-reference)
11. [Security & Governance](#11-security--governance)
12. [Project File Structure](#12-project-file-structure)
13. [Local Development Setup](#13-local-development-setup)
14. [Production Deployment (AWS)](#14-production-deployment-aws)
15. [Environment Variables](#15-environment-variables)
16. [Frontend Application](#16-frontend-application)
17. [Key Engineering Decisions](#17-key-engineering-decisions)
18. [Known Limitations & Roadmap](#18-known-limitations--roadmap)
19. [Cost Analysis](#19-cost-analysis)
20. [License & Disclaimer](#20-license--disclaimer)

---

## 1. Project Overview

The **Agentic Supplier Risk Intelligence System** is a full-stack AI SaaS application built for international trade compliance teams. It orchestrates a pipeline of five specialized AI agents — each with distinct responsibilities — to automatically evaluate the legitimacy, financial health, regulatory compliance, and reputational standing of a supplier before a business engages in a large-value trade deal.

**What makes this production-grade:**

- **Multi-agent orchestration** via LangGraph state machines — not a simple prompt chain
- **Real external data sources** — live UK Companies House API, NewsAPI, EU/OFAC/UN sanctions databases
- **RAG system** with 619 indexed chunks from real compliance PDFs, using HuggingFace embeddings
- **4-tier Role-Based Access Control (RBAC)** — super_admin, admin, analyst, viewer
- **Centralized LLM cost governance** — every GPT call logged with token counts and USD cost
- **JWT blacklisting** — proper logout invalidation, not just client-side token deletion
- **Subscription enforcement** — monthly evaluation limits by tier, checked before AI workflow triggers
- **Full Docker containerization** deployed on AWS EC2 (ap-south-1)
- **React SaaS frontend** with 10 pages, deployed on AWS S3 static hosting

**Live Demo:** [http://agentic-supplier-risk-frontend-786.s3-website.ap-south-1.amazonaws.com/platform-admin](http://agentic-supplier-risk-frontend-786.s3-website.ap-south-1.amazonaws.com/platform-admin)

---

## 2. The Business Problem

When a company wants to onboard an international supplier for a large-value trade deal, a compliance team must answer these questions before signing any contract:

| Question | What It Requires |
|----------|-----------------|
| Is this company legally registered and active? | Company registry lookups |
| Are there any sanctions, watchlist, or fraud concerns? | EU, OFAC, UN sanctions database checks |
| Is their financial documentation credible and consistent? | Manual document review |
| What is their public reputation? | News media searches and sentiment analysis |
| Are their export/import licenses valid and compliant? | Regulatory policy knowledge |

**Traditional process:** A compliance analyst manually checks each of these — visiting government portals, reading PDF documents, searching news archives — taking **2–3 business days per supplier.**

**This system:** Automates the entire pipeline in **~10 minutes** with full audit trails, explainable AI reasoning, and structured output.

---

## 3. Real-World Usage Scenario

> **Persona:** Ravi — a textile business owner based in India who wants to import clothing from a US-based manufacturer, *TechTextiles Ltd.*

**Step-by-step flow:**

1. Ravi logs into the SaaS application
2. Creates a supplier profile: company name, registration number, country
3. Uploads supplier documents: registration certificate, financial statements, export licenses, VAT certificate
4. Selects documents, writes business context, clicks **"Start Evaluation"**
5. The 5-agent pipeline executes asynchronously (~10 minutes)
6. Ravi receives this structured output:

```json
{
  "risk_level": "Medium",
  "confidence_score": 0.78,
  "reasoning": "Company is registered and active with positive news coverage. However, missing VAT certificate raises compliance concerns. Address inconsistency between invoice and registration documents requires clarification.",
  "recommended_actions": [
    "Request VAT registration certificate",
    "Clarify registered address discrepancy",
    "Proceed with onboarding pending document verification"
  ],
  "risk_factors": {
    "positive": ["Active company registration", "Positive news coverage", "No sanctions matches"],
    "negative": ["Missing VAT certificate", "Address inconsistency across documents"]
  }
}
```

7. Ravi also receives a completion email via Resend API
8. The full evaluation report — with document analysis, external intelligence, compliance citations, and evidence timeline — is available in the dashboard

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React 18)                          │
│              AWS S3 Static Hosting (ap-south-1)                 │
│         Vite + Tailwind CSS + shadcn/ui + Framer Motion         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP REST API (Axios + JWT)
                           │ CORS-validated requests
┌──────────────────────────▼──────────────────────────────────────┐
│                     FASTAPI BACKEND                             │
│                  AWS EC2 m7i-flex.large                         │
│         Docker Container — port 8000                            │
│   ┌─────────────┬──────────────┬────────────────────────────┐   │
│   │  Auth Layer │  CRUD Routes │  Background Job Dispatch   │   │
│   │  (JWT+bcrypt│  (26 endpoints│  (Celery-style async eval) │   │
│   └─────────────┴──────────────┴────────────────────────────┘   │
└───┬──────────┬──────────────┬────────────────┬──────────────────┘
    │          │              │                │
    ▼          ▼              ▼                ▼
PostgreSQL   Redis          MinIO          LangGraph
(postgres)  (redis)        (minio)        Workflow
port 5432   port 6379     port 9000       Engine
    │          │              │                │
    │    JWT Blacklist    PDF Storage    ┌──────▼─────────────┐
    │    Rate Limiting    (S3-compat)   │   5-Agent Pipeline  │
    │    RAG Cache                      │  Planner→Document→  │
    │                                   │  RAG→External→      │
    │                                   │  Decision           │
    │                                   └──────┬──────────────┘
    │                                          │
    │                          ┌───────────────┼───────────────┐
    │                          ▼               ▼               ▼
    │                   Document Tools    RAG System     External Tools
    │                   (PyPDF2/         (Qdrant +       (NewsAPI /
    │                   pdfplumber)      HuggingFace)    CompaniesHouse /
    │                                    port 6333       Sanctions DB)
    │
    └── usage_tracking table (cost per GPT call logged)
```

---

### 4.2 Low-Level Component Architecture

```
AGENTIC SUPPLIER RISK INTELLIGENCE SYSTEM
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────┐
  │                    API LAYER (FastAPI)                        │
  │                                                              │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
  │  │  /auth/* │  │/suppliers│  │/evaluations  │ /api/admin │  │
  │  │ signup   │  │  CRUD    │  │ POST/GET  │  │ 8 endpoints│  │
  │  │ login    │  │ 5 endpoints  │ rate-limited  super_admin │  │
  │  │ logout   │  │          │  │          │  │ only       │  │
  │  │ /me      │  └──────────┘  └──────────┘  └────────────┘  │
  │  └──────────┘                                               │
  │                                                              │
  │  ┌──────────────────────────────────────────────────────┐   │
  │  │                 MIDDLEWARE LAYER                      │   │
  │  │  JWT Validation → Blacklist Check → Role Check →     │   │
  │  │  Rate Limit Check → Subscription Check → Handler     │   │
  │  └──────────────────────────────────────────────────────┘   │
  └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌──────────────────────────────────────────────────────────────┐
  │               SERVICE LAYER                                  │
  │  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐  │
  │  │  LLMService    │  │ EmailService │  │  RateLimiter    │  │
  │  │  - Single OAI  │  │  - Resend    │  │  - Redis        │  │
  │  │    client      │  │    API       │  │    counters     │  │
  │  │  - Cost track  │  │  - Non-      │  │  - JWT          │  │
  │  │  - Token log   │  │    blocking  │  │    blacklist    │  │
  │  │  - usage_track │  │              │  │  - Fail-open    │  │
  │  └────────────────┘  └──────────────┘  └─────────────────┘  │
  └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌──────────────────────────────────────────────────────────────┐
  │           LANGGRAPH ORCHESTRATION LAYER                      │
  │                                                              │
  │   StateGraph (TypedDict state accumulates across agents)     │
  │                                                              │
  │   ┌─────────┐   ┌──────────┐   ┌────────┐   ┌──────────┐   │
  │   │ Planner │──▶│ Document │──▶│  RAG   │──▶│ External │   │
  │   │ Agent   │   │  Agent   │   │ Agent  │   │  Agent   │   │
  │   └─────────┘   └──────────┘   └────────┘   └──────────┘   │
  │                                                    │         │
  │                                             ┌──────▼──────┐  │
  │                                             │  Decision   │  │
  │                                             │   Agent     │  │
  │                                             └──────┬──────┘  │
  │                                                    │ END      │
  └────────────────────────────────────────────────────┼─────────┘
                                                        │
                                                        ▼
                                              Final Risk Assessment
                                              Saved to PostgreSQL
```

---

### 4.3 Database Architecture & Connections

```
╔══════════════════════════════════════════════════════════════════════╗
║                    DATABASE ARCHITECTURE                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │              PostgreSQL 15  (primary relational)             │    ║
║  │              Internal: postgres:5432                         │    ║
║  │                                                              │    ║
║  │  ┌──────────┐    ┌─────────┐    ┌────────────────────────┐  │    ║
║  │  │companies │───▶│  users  │    │      evaluations       │  │    ║
║  │  │ company  │    │ user_id │◀───│  evaluation_id         │  │    ║
║  │  │ _id (PK) │    │ company │    │  supplier_id (FK)      │  │    ║
║  │  │ name     │    │ _id(FK) │    │  company_id (FK)       │  │    ║
║  │  │ tier     │    │ email   │    │  risk_level            │  │    ║
║  │  │ max_users│    │ role    │    │  confidence_score      │  │    ║
║  │  │ is_active│    │ pw_hash │    │  reasoning (TEXT)      │  │    ║
║  │  └──────────┘    └─────────┘    │  agent_outputs (JSONB) │  │    ║
║  │        │               │        │  openai_cost_usd       │  │    ║
║  │        │               │        └────────────────────────┘  │    ║
║  │        │               │                   │                 │    ║
║  │        ▼               ▼                   ▼                 │    ║
║  │  ┌──────────┐   ┌──────────────┐  ┌───────────────────────┐ │    ║
║  │  │suppliers │   │usage_tracking│  │      documents        │ │    ║
║  │  │supplier  │   │ company_id   │  │  document_id          │ │    ║
║  │  │ _id (PK) │   │ eval_id      │  │  supplier_id (FK)     │ │    ║
║  │  │ company  │   │ agent_name   │  │  file_path (MinIO)    │ │    ║
║  │  │ _id (FK) │   │ model_name   │  │  extracted_data(JSONB)│ │    ║
║  │  │ name     │   │ prompt_tokens│  └───────────────────────┘ │    ║
║  │  │ country  │   │ total_cost   │                             │    ║
║  │  │ risk_lvl │   └──────────────┘                             │    ║
║  │  └──────────┘                                                │    ║
║  │                                                              │    ║
║  │  ┌──────────────┐  ┌─────────────┐  ┌────────────────────┐  │    ║
║  │  │ rag_documents│  │  api_keys   │  │   notifications    │  │    ║
║  │  │ doc_id       │  │ company_id  │  │  notification_id   │  │    ║
║  │  │ doc_name     │  │ api_key_hash│  │  type              │  │    ║
║  │  │ chunk_count  │  │ rate_limit  │  │  status (pending/  │  │    ║
║  │  │ last_indexed │  └─────────────┘  │  sent/failed)      │  │    ║
║  │  └──────────────┘                   └────────────────────┘  │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║                                                                      ║
║  ┌─────────────────────┐  ┌──────────────────────────────────────┐  ║
║  │    Redis 7           │  │           Qdrant                      │  ║
║  │  redis:6379          │  │         qdrant:6333                   │  ║
║  │                      │  │                                       │  ║
║  │  [hash] jwt:blacklist│  │  Collection: compliance_policies      │  ║
║  │  [counter] ratelimit │  │  Dimensions: 768                      │  ║
║  │  [string] rag_cache  │  │  Distance: Cosine Similarity          │  ║
║  │                      │  │  Chunks: 619                          │  ║
║  │  TTL = JWT expiry    │  │  Embedding: all-mpnet-base-v2         │  ║
║  │  (24h per token)     │  │                                       │  ║
║  └─────────────────────┘  └──────────────────────────────────────┘  ║
║                                                                      ║
║  ┌────────────────────────────────────────────────────────────────┐  ║
║  │                         MinIO                                  │  ║
║  │                      minio:9000                                │  ║
║  │                                                                │  ║
║  │  Bucket: supplier-documents                                    │  ║
║  │  Stores: Uploaded supplier PDFs                                │  ║
║  │  Access: Presigned URLs via FastAPI                            │  ║
║  │  Metadata: Stored in PostgreSQL documents table                │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

### 4.4 Container Network Architecture

All services run within a single Docker Compose network on AWS EC2:

```
╔═══════════════════════════════════════════════════════════════╗
║            AWS EC2 m7i-flex.large — ap-south-1                ║
║                                                               ║
║  ┌──────────────────────────────────────────────────────┐    ║
║  │          Docker Bridge Network                        │    ║
║  │          supplier_risk_network                        │    ║
║  │                                                       │    ║
║  │  ┌─────────┐  ┌─────────┐  ┌────────┐  ┌─────────┐  │    ║
║  │  │   api   │  │postgres │  │ redis  │  │ qdrant  │  │    ║
║  │  │ :8000   │  │  :5432  │  │  :6379 │  │  :6333  │  │    ║
║  │  └────┬────┘  └────┬────┘  └───┬────┘  └────┬────┘  │    ║
║  │       │            │           │              │       │    ║
║  │       └────────────┴───────────┴──────────────┘       │    ║
║  │                   Internal DNS                         │    ║
║  │              (container names = hostnames)             │    ║
║  │                                                       │    ║
║  │  ┌─────────┐                                          │    ║
║  │  │  minio  │                                          │    ║
║  │  │  :9000  │                                          │    ║
║  │  └─────────┘                                          │    ║
║  └──────────────────────────────────────────────────────┘    ║
║                                                               ║
║  Security Group (Publicly Exposed):                           ║
║  ✅ Port 80   — HTTP                                          ║
║  ✅ Port 443  — HTTPS (future)                                ║
║  ✅ Port 8000 — FastAPI                                       ║
║                                                               ║
║  Security Group (Internal Only):                              ║
║  🔒 Port 5432 — PostgreSQL                                    ║
║  🔒 Port 6379 — Redis                                         ║
║  🔒 Port 6333 — Qdrant                                        ║
║  🔒 Port 9000 — MinIO                                         ║
╚═══════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────┐
  │     AWS S3 — Static Hosting         │
  │  agentic-supplier-risk-frontend-786 │
  │  Region: ap-south-1                 │
  │  React SPA (dist/ build)            │
  │  VITE_API_URL → EC2 public IP:8000  │
  └─────────────────────────────────────┘
```

---

## 5. The 5-Agent Agentic Workflow

The system uses **LangGraph** to orchestrate a sequential state machine. Each agent receives the accumulated state from prior agents, adds its own output, and passes the enriched state forward.

### 5.1 Workflow Orchestration Diagram

```
INPUT: { supplier_name, country, registration_number,
         document_ids[], business_context }
         
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LANGGRAPH STATE MACHINE                   │
│                                                             │
│  State: EvaluationState (TypedDict — accumulated across     │
│         all 5 agents)                                       │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
╔════════════════════════════════╗
║      AGENT 1: PLANNER          ║
║  agents/planner_agent.py       ║
╠════════════════════════════════╣
║  Input:  business scenario     ║
║  Model:  GPT-4o-mini           ║
║  Output: 5–8 evaluation tasks  ║
║  Cost:   tracked to DB         ║
╚══════════════╤═════════════════╝
               │ tasks list passed in state
               ▼
╔════════════════════════════════╗
║    AGENT 2: DOCUMENT           ║
║  agents/document_agent.py      ║
╠════════════════════════════════╣
║  Input:  PDF document IDs      ║
║  Tools:  MCP-1 (read_pdf,      ║
║          extract_tables)       ║
║  Model:  GPT-4o-mini           ║
║  Output: extracted_data,       ║
║          missing_data[],       ║
║          inconsistencies[]     ║
║  Cost:   tracked to DB         ║
╚══════════════╤═════════════════╝
               │ document findings passed in state
               ▼
╔════════════════════════════════╗
║    AGENT 3: RAG KNOWLEDGE      ║
║  agents/rag_agent.py           ║
╠════════════════════════════════╣
║  Input:  compliance questions  ║
║          from Planner tasks    ║
║  Vector: Qdrant (619 chunks)   ║
║  Embed:  HuggingFace           ║
║          all-mpnet-base-v2     ║
║  Model:  GPT-4o-mini           ║
║  Output: policy answers with   ║
║          citations (doc, page, ║
║          confidence)           ║
║  Cost:   tracked to DB         ║
╚══════════════╤═════════════════╝
               │ compliance answers passed in state
               ▼
╔════════════════════════════════╗
║  AGENT 4: EXTERNAL INTEL       ║
║  agents/external_agent.py      ║
╠════════════════════════════════╣
║  Input:  company name,         ║
║          registration number   ║
║  Tools:  MCP-2 NewsAPI         ║
║          MCP-3 Companies House ║
║          MCP-4 Sanctions Check ║
║  Output: registry_status,      ║
║          news_signals[],       ║
║          sanctions_check,      ║
║          watchlist_check       ║
╚══════════════╤═════════════════╝
               │ all signals passed in state
               ▼
╔════════════════════════════════╗
║  AGENT 5: DECISION & REPORT    ║
║  agents/decision_agent.py      ║
╠════════════════════════════════╣
║  Input:  outputs from all      ║
║          4 prior agents        ║
║  Model:  GPT-4o-mini           ║
║          (engineered prompt)   ║
║  Output: risk_level            ║
║          confidence_score      ║
║          reasoning             ║
║          recommended_actions[] ║
║          risk_factors{}        ║
║  Cost:   tracked to DB         ║
╚══════════════╤═════════════════╝
               │
               ▼
       ┌────────────────┐
       │   FINAL RESULT │
       │  Saved to:     │
       │  PostgreSQL    │
       │  evaluations   │
       │  table         │
       └────────┬───────┘
                │
                ├──▶ Email notification (Resend API)
                ├──▶ usage_tracking rows inserted
                └──▶ Frontend polling detects
                     "completed" status → renders report
```

---

### 5.2 Agent 1 — Planner Agent

**File:** `agents/planner_agent.py`

**Responsibility:** Strategic decomposition of the evaluation scenario into an ordered list of 5–8 concrete tasks. It acts as the "manager" — deciding *what* needs to be investigated without performing any investigation itself.

**Design principles:**
- Does NOT read documents, call external APIs, or make risk judgments
- Pure reasoning agent — takes business context, produces a task plan
- Mock mode available for zero-cost unit testing

**Example output:**
```json
{
  "tasks": [
    "Verify company registration status in UK Companies House",
    "Analyze financial statements for consistency and red flags",
    "Check for negative news coverage in last 12 months",
    "Validate export license against UK export control regulations",
    "Cross-reference company name against EU/OFAC/UN sanctions lists",
    "Verify VAT registration status",
    "Check for address consistency across all submitted documents"
  ]
}
```

---

### 5.3 Agent 2 — Document Intelligence Agent

**File:** `agents/document_agent.py`

**Responsibility:** Extract structured, machine-readable facts from supplier-submitted PDF documents. Identifies what data is present, what is missing, and what appears inconsistent across documents.

**Tools used:** MCP-1 (Document Tools)
- `read_pdf(file_path)` — PyPDF2 with pymupdf fallback
- `extract_tables(file_path, page_numbers)` — pdfplumber

**Design principles:**
- Extracts facts, does NOT make risk judgments
- Explicitly flags missing required documents (e.g. no VAT certificate)
- Explicitly flags cross-document inconsistencies (e.g. address on invoice ≠ address on registration)

---

### 5.4 Agent 3 — RAG Knowledge Agent

**File:** `agents/rag_agent.py`

**Responsibility:** Answer compliance policy questions by querying an internal vector knowledge base built from real regulatory and trade documentation. Provides answers with explicit source citations.

**RAG Pipeline:**
```
4 Compliance PDFs → PyPDF2 extraction → ~700-token chunks (100 overlap)
→ HuggingFace all-mpnet-base-v2 embeddings (768-dim, FREE, local)
→ Qdrant vector store → top-5 semantic matches retrieved
→ GPT-4o-mini generates answer with citation (document name, page, confidence)
```

**Why HuggingFace over OpenAI embeddings:** OpenAI charges per token; for 200+ page regulatory PDFs queried repeatedly, costs compound. HuggingFace runs entirely locally = $0 forever with comparable quality.

**Critical implementation detail:** Qdrant client connects to `qdrant:6333` in production (Docker container hostname). In development, hardcoded to `127.0.0.1:6333` instead of `localhost` to avoid a Windows DNS resolution bug where Python caches `localhost` at module import time, causing `[Errno 11001] getaddrinfo failed`.

---

### 5.5 Agent 4 — External Intelligence Agent

**File:** `agents/external_agent.py`

**Responsibility:** Gather external risk signals from live, authoritative sources. Returns signals — not conclusions. The Decision Agent makes the final judgment.

**Tools used:**
- **MCP-2 (NewsAPI):** Live news search with keyword-based sentiment analysis. Falls back to mock if no API key.
- **MCP-3 (UK Companies House):** Live government public API — company status, registration date, filing history. No authentication required.
- **MCP-4 (Sanctions Check):** Cross-references company name against combined real government sanctions data: 276 EU entities + 6,403 OFAC/UN individuals, parsed from official CSV/XML sources.

---

### 5.6 Agent 5 — Decision & Report Agent

**File:** `agents/decision_agent.py`

**Responsibility:** The synthesis layer. Receives all outputs from Agents 1–4 and produces a final, explainable risk assessment using carefully engineered GPT-4o-mini prompts.

**Output structure:**
```json
{
  "risk_level": "Low | Medium | High",
  "confidence_score": 0.0–1.0,
  "reasoning": "Detailed natural language explanation",
  "recommended_actions": ["Action 1", "Action 2", "..."],
  "risk_factors": {
    "positive": ["Factor 1", "Factor 2"],
    "negative": ["Factor 1", "Factor 2"]
  }
}
```

**Design principle:** Instruction-tuned prompts only — no fine-tuning. The LLM is guided via structured system prompts with explicit output format requirements.

---

## 6. MCP Tool Groups

**MCP (Model Context Protocol)** in this system refers to the separation of concerns between agents (which decide *when* and *why* to use a tool) and tool implementations (which define *how* to execute the action). This mirrors real-world AI agent architectures.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP TOOL ARCHITECTURE                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MCP-1: Document Tools  (mcp_tools/document_tools.py)   │   │
│  │                                                         │   │
│  │  read_pdf(file_path)                                    │   │
│  │    → PyPDF2 primary, pymupdf fallback                   │   │
│  │    → Returns: raw text per page                         │   │
│  │                                                         │   │
│  │  extract_tables(file_path, page_numbers)                │   │
│  │    → pdfplumber for structured table extraction         │   │
│  │    → Returns: list of dicts per table row               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MCP-2: News Tools  (mcp_tools/news_tools.py)           │   │
│  │                                                         │   │
│  │  search_news(company_name, date_range, max_results)     │   │
│  │    → NewsAPI (FREE tier: 100 req/day)                   │   │
│  │    → Fallback to mock data if NEWSAPI_KEY absent        │   │
│  │                                                         │   │
│  │  analyze_sentiment(article_text)                        │   │
│  │    → Keyword-based sentiment: positive/negative/neutral │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MCP-3: Registry Tools  (mcp_tools/registry_tools.py)   │   │
│  │                                                         │   │
│  │  check_uk_companies_house(registration_number)          │   │
│  │    → UK Government public search endpoint (no auth)     │   │
│  │    → Returns: status, incorporation date, filing status │   │
│  │    → Previous bug: 401 from wrong endpoint — fixed by   │   │
│  │      switching to public search endpoint                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MCP-4: Sanctions Tools  (mcp_tools/sanctions_tools.py) │   │
│  │                                                         │   │
│  │  check_sanctions_list(company_name, owner_names)        │   │
│  │    → EU Consolidated Sanctions (eu_sanctions.csv)       │   │
│  │    → OFAC SDN List (ofac_sdn.csv)                       │   │
│  │    → UN Consolidated List (un_sanctions.xml)            │   │
│  │    → Combined: 276 entities + 6,403 individuals         │   │
│  │    → Parsed by: mcp_tools/sanctions_data_loader.py      │   │
│  │                                                         │   │
│  │  check_watchlist(registration_number, country)          │   │
│  │    → Risk watchlist cross-reference                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. RAG System

The RAG (Retrieval-Augmented Generation) system gives Agent 3 authoritative, citation-backed answers from real compliance documents — rather than relying on potentially outdated or hallucinated LLM knowledge.

### Knowledge Base Documents

| Document | Domain |
|----------|--------|
| `Customer_Guide_Booklet_EN.pdf` | General trade customer guidance |
| `guide_to_exporting.pdf` | UK export process and requirements |
| `OECD Due Diligence Guidance for Responsible Business.pdf` | International due diligence standards |
| `uk_export_control_list_2025.pdf` | UK export control regulations 2025 |

### Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                      RAG INGESTION PIPELINE                      │
│                    (rag/ingest_pipeline.py)                      │
│                                                                  │
│  4 Source PDFs                                                   │
│       │                                                          │
│       ▼                                                          │
│  PyPDF2 text extraction (page-by-page)                           │
│       │                                                          │
│       ▼                                                          │
│  Chunking: ~700 tokens per chunk, ~100 token overlap             │
│  → 619 total chunks                                              │
│       │                                                          │
│       ▼                                                          │
│  HuggingFace all-mpnet-base-v2 embeddings                        │
│  → 768-dimensional dense vectors                                 │
│  → Runs locally, zero API cost                                   │
│       │                                                          │
│       ▼                                                          │
│  Qdrant storage (collection: compliance_policies)                │
│  → Cosine similarity indexing                                    │
│  → Payload: {text, doc_name, page_number, chunk_index}           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     RAG RETRIEVAL PIPELINE                       │
│                      (rag/retrieval.py)                          │
│                                                                  │
│  Compliance question (from Planner tasks)                        │
│       │                                                          │
│       ▼                                                          │
│  Check Redis cache (avoid redundant queries → cost savings)      │
│       │                                                          │
│       ▼ (cache miss)                                             │
│  Embed question → 768-dim vector                                 │
│       │                                                          │
│       ▼                                                          │
│  Qdrant cosine similarity search → top-5 chunks                  │
│       │                                                          │
│       ▼                                                          │
│  GPT-4o-mini: "Answer using ONLY these retrieved chunks."        │
│  → Answer with citation: {doc_name, page, confidence}            │
│       │                                                          │
│       ▼                                                          │
│  Store in Redis cache (TTL: 24h)                                 │
│       │                                                          │
│       ▼                                                          │
│  Return structured response to Agent 3                           │
└──────────────────────────────────────────────────────────────────┘
```

**Why Qdrant over FAISS:** FAISS is in-memory only with no persistence — suitable for research notebooks. Qdrant supports full CRUD operations, metadata filtering, persistent storage on disk, and production-grade horizontal scaling. For a SaaS system that re-indexes on deployment and needs consistent queries across restarts, Qdrant is the correct choice.

---

## 8. Tech Stack

### Backend

| Technology | Version | Purpose | Cost |
|------------|---------|---------|------|
| Python | 3.10 | Core language | Free |
| FastAPI | 0.115.6 | REST API framework, auto Swagger docs | Free |
| LangGraph | 0.2.52 | Multi-agent state machine orchestration | Free |
| langchain-core | 0.3.21 | LLM integration primitives | Free |
| langchain-openai | 0.2.9 | OpenAI LangChain integration | Free |
| OpenAI GPT-4o-mini | — | LLM for all 5 agents | ~$5–10/month |
| HuggingFace sentence-transformers | 3.3.1 | Local embeddings (all-mpnet-base-v2, 768-dim) | Free |
| Qdrant | latest (Docker) | Vector database — 619 chunks, cosine similarity | Free |
| PostgreSQL | 15 (Docker) | Primary relational store — 9 tables | Free |
| Redis | 7 (Docker) | JWT blacklist, rate limiting, RAG cache | Free |
| MinIO | latest (Docker) | S3-compatible object storage for PDFs | Free |
| Celery | 5.4.0 | Async background job processing | Free |
| PyJWT | 2.9.0 | JWT token creation and validation | Free |
| bcrypt | 4.2.1 | Password hashing | Free |
| PyPDF2 | 3.0.1 | PDF text extraction | Free |
| pdfplumber | 0.11.4 | PDF table extraction | Free |
| pymupdf | 1.24.14 | PyPDF2 fallback for complex PDFs | Free |
| SQLAlchemy | — | ORM + connection pooling | Free |
| pydantic-settings | 2.6.1 | Environment variable management | Free |
| requests | 2.32.3 | External API HTTP calls | Free |
| redis (client) | 5.2.1 | Redis Python client | Free |
| Resend API | — | Transactional email notifications | Free tier |
| pytest | 8.3.4 | Unit testing framework | Free |
| pytest-asyncio | 0.24.0 | Async test support | Free |
| httpx | 0.28.1 | FastAPI test client | Free |

### Frontend

| Technology | Version | Purpose | Cost |
|------------|---------|---------|------|
| React | 18 | UI framework | Free |
| Vite | — | Build tool and dev server | Free |
| Tailwind CSS | — | Utility-first CSS framework | Free |
| shadcn/ui | — | Accessible component library | Free |
| Framer Motion | — | Scroll animations and page transitions | Free |
| Recharts | — | Risk distribution charts, cost trend charts | Free |
| TanStack Query | — | Server state management and caching | Free |
| React Router | v6 | Client-side routing | Free |
| Axios | — | HTTP client with interceptors | Free |
| React Hook Form | — | Form state management | Free |
| jwt-decode | — | Client-side JWT decoding for role checks | Free |
| Lucide React | — | Icon library | Free |

### Infrastructure

| Technology | Version | Purpose | Cost |
|------------|---------|---------|------|
| Docker Desktop | 29.2.0 | Containerization | Free |
| Docker Compose | v5.0.2 | Multi-container orchestration | Free |
| AWS EC2 | m7i-flex.large | Backend hosting (ap-south-1) | ~$60–80/month |
| AWS S3 | — | React SPA static hosting | ~$0.50/month |
| Prometheus | — | Metrics collection | Free |
| Grafana | — | Metrics visualization | Free |

**Total monthly cost: ~$65–90 (EC2 + OpenAI + S3). All other components are free.**

---

## 9. Database Schema

### PostgreSQL — 9 Tables

```sql
-- Multi-tenancy: every record scoped to a company
companies (
  company_id UUID PRIMARY KEY,
  company_name VARCHAR(255) UNIQUE NOT NULL,
  subscription_tier VARCHAR(50) DEFAULT 'free',  -- free/standard/premium
  max_users INTEGER DEFAULT 5,
  is_active BOOLEAN DEFAULT true
)

-- 4-tier RBAC
users (
  user_id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'viewer',  -- super_admin/admin/analyst/viewer
  is_active BOOLEAN DEFAULT true
)

suppliers (
  supplier_id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies,
  supplier_name VARCHAR(255) NOT NULL,
  country VARCHAR(100),
  registration_number VARCHAR(100),
  risk_level VARCHAR(50)  -- Low/Medium/High
)

evaluations (
  evaluation_id UUID PRIMARY KEY,
  supplier_id UUID REFERENCES suppliers,
  company_id UUID REFERENCES companies,
  status VARCHAR(50),  -- pending/running/completed/failed
  risk_level VARCHAR(50),
  confidence_score FLOAT,
  reasoning TEXT,
  recommended_actions JSONB,
  risk_factors JSONB,
  agent_outputs JSONB,  -- full per-agent output stored
  openai_cost_usd FLOAT,
  created_at TIMESTAMP
)

documents (
  document_id UUID PRIMARY KEY,
  supplier_id UUID REFERENCES suppliers,
  company_id UUID REFERENCES companies,
  document_type VARCHAR(100),
  original_filename VARCHAR(255),
  file_path VARCHAR(500),  -- MinIO object path
  extracted_data JSONB
)

-- LLM cost governance — 1 row per GPT call
usage_tracking (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies,
  evaluation_id UUID REFERENCES evaluations,
  agent_name VARCHAR(100),
  model_name VARCHAR(100),
  prompt_tokens INTEGER,
  completion_tokens INTEGER,
  total_tokens INTEGER,
  total_cost FLOAT,
  created_at TIMESTAMP
)

rag_documents (
  doc_id UUID PRIMARY KEY,
  document_name VARCHAR(255),
  chunk_count INTEGER,
  last_indexed TIMESTAMP
)

api_keys (
  key_id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies,
  api_key_hash VARCHAR(255),
  rate_limit_per_minute INTEGER
)

notifications (
  notification_id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies,
  evaluation_id UUID REFERENCES evaluations,
  notification_type VARCHAR(100),
  status VARCHAR(50)  -- pending/sent/failed
)
```

---

## 10. API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/signup` | Public | Register company + first admin user |
| `POST` | `/auth/login` | Public | Returns JWT token (24h expiry) |
| `GET` | `/auth/me` | Bearer JWT | Current user profile |
| `POST` | `/auth/logout` | Bearer JWT | Blacklist token in Redis |

### Suppliers

| Method | Endpoint | Roles | Description |
|--------|----------|-------|-------------|
| `POST` | `/api/suppliers/` | admin, analyst | Create supplier |
| `GET` | `/api/suppliers/` | all | List company's suppliers |
| `GET` | `/api/suppliers/{id}` | all | Get supplier details |
| `PUT` | `/api/suppliers/{id}` | admin, analyst | Update supplier |
| `DELETE` | `/api/suppliers/{id}` | admin | Delete supplier |

### Evaluations

| Method | Endpoint | Roles | Description |
|--------|----------|-------|-------------|
| `POST` | `/api/evaluations/` | admin, analyst | Trigger AI evaluation (rate-limited, subscription-checked) |
| `GET` | `/api/evaluations/` | all | List evaluations (paginated) |
| `GET` | `/api/evaluations/{id}` | all | Get evaluation + full agent outputs |

### Documents

| Method | Endpoint | Roles | Description |
|--------|----------|-------|-------------|
| `POST` | `/api/documents/upload` | admin, analyst | Upload PDF to MinIO |
| `GET` | `/api/documents/?supplier_id=` | all | List documents by supplier |

### Users (RBAC Management)

| Method | Endpoint | Roles | Description |
|--------|----------|-------|-------------|
| `POST` | `/api/users/` | admin | Create analyst or viewer (subscription limit enforced) |

### Platform Admin (super_admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/usage-summary` | Total evaluations, tokens, cost (all-time + this month) |
| `GET` | `/api/admin/company-usage` | Per-company cost breakdown |
| `GET` | `/api/admin/monthly-cost` | Last 12 months cost trend |
| `GET` | `/api/admin/top-expensive-evaluations` | Anomaly detection for billing |
| `GET` | `/api/admin/companies` | All customer companies |
| `PATCH` | `/api/admin/companies/{id}/deactivate` | Soft-suspend company |
| `PATCH` | `/api/admin/companies/{id}/reactivate` | Restore suspended company |
| `DELETE` | `/api/admin/companies/{id}/permanent-delete` | GDPR deletion (requires `?confirm=DELETE_COMPANY_PERMANENTLY`) |

---

## 11. Security & Governance

### Authentication Flow
```
User submits credentials
       │
       ▼
bcrypt.verify(password, stored_hash)
       │
       ▼ (success)
JWT created: { user_id, company_id, role, exp: now+24h }
       │
       ▼
Client stores JWT in localStorage
       │
Every subsequent request:
       ▼
Authorization: Bearer <token>
       │
       ▼
get_current_user() middleware:
  1. Extract token from header
  2. Verify signature (JWT_SECRET_KEY)
  3. Check Redis blacklist (is_token_blacklisted)
  4. Decode payload → user object
  5. Pass to route handler
```

### 4-Tier RBAC

| Role | How Created | Permissions |
|------|------------|------------|
| `super_admin` | Direct DB insert (never via signup) | All endpoints + platform admin panel |
| `admin` | First user to register a company name | Full control within their company |
| `analyst` | Created by admin via `POST /api/users/` | Create suppliers, run evaluations, upload documents |
| `viewer` | Created by admin via `POST /api/users/` | Read-only access |

### LLM Cost Governance

Every GPT call flows through `LLMService`:

```
Agent requests LLM call
       │
       ▼
LLMService.call(prompt, agent_name, company_id, evaluation_id)
       │
       ▼
Single OpenAI client (initialized once, reused)
       │
       ▼
API response received
       │
       ▼
Extract: prompt_tokens, completion_tokens from response.usage
       │
       ▼
Calculate cost: (prompt_tokens × $0.00015/1K) + (completion_tokens × $0.00060/1K)
       │
       ▼
INSERT into usage_tracking (company_id, evaluation_id, agent_name,
                             model, prompt_tokens, completion_tokens,
                             total_cost)
       │
       ▼
Return structured response to agent
```

### Subscription Enforcement

```
POST /api/evaluations/ called
       │
       ▼
Check subscription tier: free(50/month) | standard(500/month) | premium(unlimited)
       │
       ├── premium? → skip count check → proceed
       │
       ▼ (free or standard)
SELECT COUNT(*) FROM evaluations WHERE company_id = ? 
  AND created_at >= date_trunc('month', now())
       │
       ├── count < limit? → proceed
       └── count >= limit? → HTTP 403 "Monthly evaluation limit reached"
```

### Rate Limiting

```python
# Redis counter per user — 10 evaluations per 60-second window
check_rate_limit(user_id, limit=10, window_seconds=60)
# → HTTP 429 with retry_after_seconds if exceeded
# → Fail-open design: if Redis is down, requests pass through
#   (availability > enforcement during outages)
```

---

## 12. Project File Structure

```
AGENTIC_SUPPLIER_RISK_AI/
│
├── agents/                             # AI agent implementations
│   ├── __init__.py
│   ├── planner_agent.py                # Agent 1 — task decomposition
│   ├── document_agent.py               # Agent 2 — PDF extraction
│   ├── rag_agent.py                    # Agent 3 — compliance RAG
│   ├── external_agent.py               # Agent 4 — news/registry/sanctions
│   └── decision_agent.py               # Agent 5 — risk synthesis
│
├── api/                                # FastAPI application
│   ├── main.py                         # App init, CORS, health, auth endpoints
│   ├── database.py                     # SQLAlchemy engine, get_db dependency
│   ├── models.py                       # Pydantic request/response models
│   ├── auth.py                         # bcrypt + JWT creation
│   ├── middleware.py                   # JWT validation, role checks, rate limiting
│   ├── services/
│   │   ├── llm_service.py              # Centralized OpenAI client + cost tracking
│   │   ├── email_service.py            # Resend API integration
│   │   └── rate_limiter.py             # Redis rate limiting + JWT blacklisting
│   └── routes/
│       ├── suppliers.py                # Supplier CRUD (5 endpoints)
│       ├── evaluations.py              # Evaluation endpoints (3 endpoints)
│       ├── documents.py                # File upload + retrieval (2 endpoints)
│       ├── users.py                    # Admin user creation (1 endpoint)
│       └── admin.py                    # Platform admin (8 endpoints, super_admin)
│
├── data/
│   ├── raw_documents/                  # Source PDFs for RAG
│   │   ├── Customer_Guide_Booklet_EN.pdf
│   │   ├── guide_to_exporting.pdf
│   │   ├── OECD Due Diligence Guidance for Responsible Business.pdf
│   │   └── uk_export_control_list_2025.pdf
│   ├── mock_external_data/
│   │   └── sanctions/                  # Real government sanctions data
│   │       ├── eu_sanctions.csv        # EU Consolidated Sanctions List
│   │       ├── ofac_sdn.csv            # US OFAC Specially Designated Nationals
│   │       ├── un_sanctions.xml        # UN Security Council Consolidated List
│   │       └── sanctions_combined.json # Parsed: 276 entities + 6,403 individuals
│   └── processed_chunks/               # Auto-generated by RAG ingestion
│
├── database/
│   └── schema.sql                      # PostgreSQL DDL — 9 tables
│
├── mcp_tools/                          # Tool implementations (MCP pattern)
│   ├── __init__.py
│   ├── document_tools.py               # MCP-1: PDF read + table extract
│   ├── news_tools.py                   # MCP-2: NewsAPI + sentiment analysis
│   ├── registry_tools.py               # MCP-3: UK Companies House API
│   ├── sanctions_tools.py              # MCP-4: Sanctions + watchlist check
│   └── sanctions_data_loader.py        # CSV/XML parser → sanctions_combined.json
│
├── monitoring/
│   └── prometheus.yml                  # Prometheus scrape configuration
│
├── rag/                                # RAG system
│   ├── __init__.py
│   ├── embeddings.py                   # HuggingFace 768-dim embedding wrapper
│   ├── ingest_pipeline.py              # PDF → chunks → embeddings → Qdrant
│   ├── retrieval.py                    # Semantic search + Redis caching
│   └── query_rag.py                    # Interactive CLI testing tool
│
├── workflows/
│   ├── __init__.py
│   ├── evaluation_workflow.py          # LangGraph state machine (5 agents)
│   └── test_real_evaluation.py         # End-to-end test (uses real API)
│
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                     # shadcn/ui base components
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.jsx         # Role-based navigation sidebar
│   │   │   │   ├── TopBar.jsx          # User info + notifications + logout
│   │   │   │   └── AppLayout.jsx       # Layout wrapper
│   │   │   ├── landing/                # Public landing page sections
│   │   │   ├── auth/                   # Login + Signup modals
│   │   │   ├── dashboard/              # Stats cards, risk chart, evaluations table
│   │   │   ├── suppliers/              # Supplier CRUD UI
│   │   │   ├── evaluations/            # 3-step wizard, loading screen, results
│   │   │   └── admin/                  # Platform admin charts + tables
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── SuppliersPage.jsx
│   │   │   ├── SupplierDetailPage.jsx
│   │   │   ├── NewEvaluationPage.jsx
│   │   │   ├── EvaluationResultsPage.jsx
│   │   │   ├── AllEvaluationsPage.jsx
│   │   │   ├── TeamPage.jsx
│   │   │   ├── SettingsPage.jsx
│   │   │   └── PlatformAdminPage.jsx
│   │   ├── services/
│   │   │   └── api.js                  # Axios instance + JWT interceptor
│   │   ├── utils/
│   │   │   ├── auth.js                 # Token helpers + role checks
│   │   │   └── formatters.js           # Date/currency/UUID formatters
│   │   ├── hooks/
│   │   │   ├── useAuth.js              # Auth state management
│   │   │   └── usePolling.js           # 3-second evaluation status polling
│   │   ├── App.jsx                     # Router + ProtectedRoute component
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── venv/                               # Python virtual environment
├── .env                                # Local development environment vars
├── .env.example                        # Environment variable template
├── .env.production                     # Production environment vars (EC2)
├── .gitignore
├── docker-compose.yml                  # 6 services (all containerized in prod)
├── Dockerfile                          # FastAPI application image
├── requirements.txt                    # Python dependencies (pinned versions)
├── README.md
├── test_env.py
├── test_rag_connection.py
└── test_rag_agent_workflow.py
```

---

## 13. Local Development Setup

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Docker Desktop** (for PostgreSQL, Redis, Qdrant, MinIO)
- **OpenAI API key**
- **Git**

### Step 1: Clone the Repository

```bash
git clone https://github.com/mohamedsahadm786/agentic_supplier_risk_ai.git
cd agentic_supplier_risk_ai
```

### Step 2: Create Python Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** First run downloads the HuggingFace `all-mpnet-base-v2` model (~400 MB). This is a one-time download.

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in the required values (see [Environment Variables](#15-environment-variables) section).

### Step 5: Start Infrastructure (Docker)

```bash
docker-compose up -d
```

This starts: PostgreSQL (port **5433** — 5432 is reserved for local PostgreSQL), Redis (6379), Qdrant (6333), MinIO (9000/9001), Prometheus, Grafana.

> **Important:** Docker PostgreSQL is mapped to port **5433** because port 5432 is typically occupied by a local PostgreSQL installation. Your `DATABASE_URL` must use `localhost:5433`.

Verify all containers are running:

```bash
docker-compose ps
```

### Step 6: Initialize Database Schema

```bash
# Connect to Docker PostgreSQL
psql -h localhost -p 5433 -U supplier_risk_user -d supplier_risk_db -f database/schema.sql
```

### Step 7: Ingest RAG Documents

```bash
python rag/ingest_pipeline.py
```

Expected output: `✅ Ingestion complete. 619 chunks stored in Qdrant.`

### Step 8: Start FastAPI Backend

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

API available at: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

### Step 9: Start React Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:5173`

### Creating a super_admin (Local)

The super_admin account must be created directly in the database — never through the signup flow:

```bash
# Start Python inside the venv
python

# Generate bcrypt hash for your password
import bcrypt
password = "your_secure_password"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hashed)
```

```sql
-- Insert super_admin company
INSERT INTO companies (company_id, company_name, subscription_tier, max_users)
VALUES (gen_random_uuid(), 'Platform Admin', 'premium', 1);

-- Insert super_admin user (use the bcrypt hash from above)
INSERT INTO users (user_id, company_id, email, password_hash, full_name, role)
VALUES (
  gen_random_uuid(),
  (SELECT company_id FROM companies WHERE company_name = 'Platform Admin'),
  'admin@yourplatform.com',
  '$2b$12$YOUR_BCRYPT_HASH_HERE',
  'Platform Administrator',
  'super_admin'
);
```

---

## 14. Production Deployment (AWS)

### Architecture

- **Backend:** AWS EC2 m7i-flex.large — ap-south-1 — Docker Compose (all services containerized)
- **Frontend:** AWS S3 static website hosting — ap-south-1

### Backend Deployment (EC2)

```bash
# 1. SSH into EC2 instance
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>

# 2. Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone repository
git clone https://github.com/mohamedsahadm786/agentic_supplier_risk_ai.git
cd agentic_supplier_risk_ai

# 5. Configure production environment
cp .env.example .env.production
# Fill in production values

# 6. Build and start all containers
docker-compose up -d --build

# 7. Run RAG ingestion inside API container
docker-compose exec api python rag/ingest_pipeline.py

# 8. Verify health
curl http://localhost:8000/health
```

**EC2 Security Group:**
- Inbound: TCP 8000 (API), TCP 80 (HTTP), TCP 443 (HTTPS future)
- All database ports (5432, 6379, 6333, 9000) — internal only, NOT exposed

### Frontend Deployment (S3)

```bash
# 1. Set production API URL
# In frontend/.env:
VITE_API_URL=http://<EC2_PUBLIC_IP>:8000

# 2. Build React application
cd frontend
npm run build
# Output: frontend/dist/

# 3. Create S3 bucket
aws s3 mb s3://agentic-supplier-risk-frontend-786 --region ap-south-1

# 4. Enable static website hosting
aws s3 website s3://agentic-supplier-risk-frontend-786 \
  --index-document index.html \
  --error-document index.html

# 5. Upload build files
aws s3 sync dist/ s3://agentic-supplier-risk-frontend-786

# 6. Set public read policy
aws s3api put-bucket-policy \
  --bucket agentic-supplier-risk-frontend-786 \
  --policy '{
    "Version":"2012-10-17",
    "Statement":[{
      "Effect":"Allow",
      "Principal":"*",
      "Action":"s3:GetObject",
      "Resource":"arn:aws:s3:::agentic-supplier-risk-frontend-786/*"
    }]
  }'
```

**Update CORS in `api/main.py`** to allow S3 website origin:

```python
origins = [
    "http://localhost:5173",
    "http://agentic-supplier-risk-frontend-786.s3-website.ap-south-1.amazonaws.com"
]
```

### Production Connection Strings (inside Docker Compose network)

```yaml
# In docker-compose.yml environment section for api service:
DATABASE_URL: postgresql://supplier_risk_user:password@postgres:5432/supplier_risk_db
REDIS_URL: redis://:password@redis:6379
QDRANT_HOST: qdrant
QDRANT_PORT: 6333
MINIO_ENDPOINT: minio:9000
```

> **Critical:** Inside Docker Compose, all services resolve each other by container name. PostgreSQL is at `postgres:5432` (internal port), NOT `localhost:5433` (that was only for host-to-container access in development).

---

## 15. Environment Variables

```bash
# ============================================================
# CORE
# ============================================================
OPENAI_API_KEY=sk-...              # OpenAI API key (required)
ENVIRONMENT=development            # development | production

# ============================================================
# DATABASE
# ============================================================
DATABASE_URL=postgresql://supplier_risk_user:password@localhost:5433/supplier_risk_db
POSTGRES_USER=supplier_risk_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=supplier_risk_db

# ============================================================
# REDIS
# ============================================================
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# ============================================================
# QDRANT
# ============================================================
QDRANT_HOST=127.0.0.1              # Use 'qdrant' in production Docker
QDRANT_PORT=6333

# ============================================================
# MINIO
# ============================================================
MINIO_ENDPOINT=localhost:9000      # Use 'minio:9000' in production Docker
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=supplier-documents

# ============================================================
# AUTH
# ============================================================
JWT_SECRET_KEY=your_very_long_random_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# ============================================================
# EXTERNAL APIS
# ============================================================
NEWSAPI_KEY=your_newsapi_key       # Optional — falls back to mock if absent
RESEND_API_KEY=re_...              # Resend transactional email

# ============================================================
# FRONTEND (.env in /frontend)
# ============================================================
VITE_API_URL=http://localhost:8000
```

---

## 16. Frontend Application

### Pages & Navigation

| Page | Route | Access | Description |
|------|-------|--------|-------------|
| Landing Page | `/` | Public | Product overview, pricing, how it works |
| Dashboard | `/dashboard` | Authenticated | Metrics, risk chart, recent evaluations |
| Suppliers | `/suppliers` | Authenticated | Supplier management table |
| Supplier Detail | `/suppliers/:id` | Authenticated | Documents, evaluation history |
| New Evaluation | `/evaluations/new` | admin, analyst | 3-step evaluation wizard |
| Evaluation Results | `/evaluations/:id` | Authenticated | Full AI risk report |
| All Evaluations | `/evaluations` | Authenticated | Paginated evaluations list |
| Team | `/team` | admin | User management |
| Settings | `/settings` | Authenticated | Profile + password + logout |
| Platform Admin | `/platform-admin` | super_admin | Cost analytics + company management |

### Evaluation Wizard Flow

```
Step 1: Select Supplier
  → Dropdown shows supplier names (UUID stored invisibly)
  → Pre-selects if ?supplier_id= in URL

Step 2: Select Documents
  → Fetches GET /api/documents/?supplier_id={id}
  → Checkboxes show filename, store document_id
  → Users never see or type UUIDs

Step 3: Business Context
  → Free-text textarea for deal context
  → Summary panel shows selections
  → "Start Evaluation" → POST /api/evaluations/

Loading Screen:
  → Animated 5-step progress display
  → usePolling hook: GET /api/evaluations/{id} every 3 seconds
  → On status=completed → auto-redirect to results

Results Page:
  → Risk hero banner (red/yellow/green gradient)
  → Confidence score + date
  → Full reasoning paragraph
  → Positive/negative risk factors (2-column)
  → Numbered recommended actions
  → Expandable accordions: Document Analysis, External Intel, Compliance Citations
  → Evidence trail timeline
  → Cost shown to admin/super_admin only
```

### Design System

- **Background (landing):** Deep dark navy `#0A0F1E`
- **Background (dashboard):** Light `#F9FAFB`
- **Primary accent:** Electric blue `#3B82F6`
- **Secondary accent:** Cyan `#06B6D4`
- **Risk High:** Red `#EF4444`
- **Risk Medium:** Amber `#F59E0B`
- **Risk Low:** Green `#10B981`
- **Style:** Glassmorphism cards on landing, clean SaaS cards on dashboard
- **Animations:** Framer Motion scroll-triggered entry animations
- **Typography:** Inter / Plus Jakarta Sans

---

## 17. Key Engineering Decisions

### Why LangGraph over a simple prompt chain?

LangGraph provides a **typed state machine** where each agent receives the full accumulated state from all prior agents, adds its own output, and the state object is immutable and traceable. A simple prompt chain is a single monolithic LLM call — no separation of concerns, no per-agent testability, no structured intermediate outputs. LangGraph also provides built-in error handling where one agent failure doesn't crash the entire workflow.

### Why HuggingFace embeddings over OpenAI embeddings?

OpenAI's `text-embedding-ada-002` costs $0.0001 per 1K tokens. For 619 chunks averaging 700 tokens each, that's ~$0.04 per re-indexing run. Multiplied across hundreds of queries per day and multiple re-indexing events, costs compound. HuggingFace `all-mpnet-base-v2` runs entirely locally — zero API cost forever — with 768-dimensional embeddings that provide comparable semantic quality for regulatory compliance text.

### Why Qdrant over FAISS?

FAISS (Facebook AI Similarity Search) is an in-memory research library — it has no persistence (data lost on restart), no CRUD operations (can't update individual vectors), and no metadata filtering. Qdrant is a production vector database supporting persistent storage, full CRUD, payload filtering, and horizontal scaling. For a SaaS system that needs to re-index on deployment and serve consistent queries across container restarts, FAISS is architecturally inappropriate.

### Why PostgreSQL port 5433 in development?

Standard PostgreSQL installations occupy port 5432 on the host machine. If Docker also tries to bind port 5432, there's a conflict. The solution is to map Docker PostgreSQL to 5433 (`5433:5432` in docker-compose.yml). This is a development-only concern — inside the Docker network, all containers use the internal port 5432.

### Why JWT blacklisting via Redis?

JWTs are stateless by design — a token remains cryptographically valid until its expiry, regardless of whether the user has "logged out" on the client. Without server-side blacklisting, a stolen token remains usable for its full 24-hour lifetime after a user's logout. Redis blacklisting stores token signatures with TTL equal to the JWT's remaining lifetime — making logout truly effective.

### Why fail-open on rate limiting?

If Redis is unavailable, the rate limiter is designed to **allow requests through** rather than block them. The reasoning: if Redis goes down, denying all API access to users creates a complete service outage. The trade-off (temporarily allowing slightly above the rate limit) is far less damaging to user experience than a full outage. Redis downtime events are rare and brief; availability is prioritized over strict enforcement during infrastructure incidents.

### Why MCP pattern for tool groups?

Separating agent logic (when/why to use a tool) from tool implementation (how to execute it) follows the **single responsibility principle**. Agents don't know or care how UK Companies House API authentication works — they call `check_uk_companies_house(reg_number)` and receive structured data. This makes tools independently testable, replaceable (e.g., swap NewsAPI for a different news provider without touching agent code), and interchangeable across multiple agents.

---

## 18. Known Limitations & Roadmap

### Current Limitations

| Limitation | Impact | Planned Fix |
|-----------|--------|-------------|
| MinIO files not deleted on company permanent-delete | Orphaned PDFs in storage | Phase 12: Add MinIO cleanup to delete cascade |
| JWT blacklist fail-open | Stolen tokens briefly valid if Redis down | Acceptable trade-off documented |
| No HTTPS on EC2 | Data in transit not encrypted | Phase 12: Nginx + Let's Encrypt |
| UK Companies House only | Registry check limited to UK suppliers | Phase 13: Add US SEC EDGAR, India MCA |
| NewsAPI free tier (100 req/day) | Rate limited in high-volume usage | Phase 13: Upgrade to paid tier |
| No Celery worker (evaluation is async in same process) | Long evaluations could timeout | Phase 13: Proper Celery worker queue |
| super_admin can't self-serve password reset | Manual DB operation required | Phase 12 |
| S3 static hosting (no CDN) | Slower for international users | Phase 11: CloudFront distribution |

### Roadmap

- **Phase 12:** Nginx reverse proxy, HTTPS/SSL, CloudWatch alarms, Docker log rotation, automated daily PostgreSQL backups, EC2 instance scheduling
- **Phase 13:** Additional company registry integrations (US, India, EU), Celery distributed workers, multi-region deployment, API rate limit upgrade
- **Phase 14:** White-label multi-tenant customization, webhook support, CSV/Excel report export, Slack integration for risk alerts

---

## 19. Cost Analysis

### Monthly Operating Costs

| Component | Service | Estimated Monthly Cost |
|-----------|---------|----------------------|
| LLM inference | OpenAI GPT-4o-mini | $5–10 |
| Compute | AWS EC2 m7i-flex.large | ~$60–80 |
| Frontend hosting | AWS S3 static | ~$0.50 |
| Email | Resend API (free tier: 3,000/month) | $0 |
| News API | NewsAPI free tier (100 req/day) | $0 |
| All databases | Docker on EC2 (PostgreSQL, Redis, Qdrant, MinIO) | Included in EC2 |
| **Total** | | **~$65–90/month** |

### Cost Optimization in Architecture

1. **HuggingFace embeddings** — $0 vs ~$0.04–$0.10/day with OpenAI embeddings
2. **Redis RAG caching** — Repeated compliance questions served from cache, not GPT — saves ~80% of Agent 3 LLM calls
3. **GPT-4o-mini** — ~10× cheaper than GPT-4o, adequate quality for structured extraction and synthesis tasks
4. **Subscription enforcement before AI trigger** — Free-tier users exceeding limits are blocked before any API cost is incurred
5. **Mock mode in all agents** — Development and unit testing incur $0 in API costs

---

## 20. License & Disclaimer

This project is released under the **MIT License** and is intended as a **portfolio and learning project** demonstrating production-grade AI engineering practices.

> ⚠️ **Important Disclaimer:** This system is a **decision-support tool**, not a legal authority for supplier compliance. Risk assessments generated by this system are based on publicly available information and AI reasoning. They should be reviewed by qualified compliance professionals before being used as the basis for any legal, financial, or contractual decisions. Sanctions data is sourced from public government lists but may not reflect real-time updates. The authors accept no liability for decisions made based on outputs from this system.

---

<div align="center">

**Built by [Mohamed Sahad](https://github.com/mohamedsahadm786)**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Visit_App-blue?style=for-the-badge)](http://agentic-supplier-risk-frontend-786.s3-website.ap-south-1.amazonaws.com/platform-admin)
[![GitHub](https://img.shields.io/badge/GitHub-mohamedsahadm786-black?style=for-the-badge&logo=github)](https://github.com/mohamedsahadm786/agentic_supplier_risk_ai)

*A portfolio project demonstrating senior-level AI engineering: multi-agent orchestration, RAG systems, production security, multi-tenant SaaS architecture, and AWS deployment.*

</div>
