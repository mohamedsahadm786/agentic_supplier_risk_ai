# 🧠 Agentic Supplier Risk Intelligence System

## Production-Grade Multi-Tenant AI SaaS for Automated Supplier Risk Evaluation

------------------------------------------------------------------------

## 🌍 Live Deployment

Frontend (AWS S3 Static Hosting):\
http://agentic-supplier-risk-frontend-786.s3-website.ap-south-1.amazonaws.com/platform-admin

Backend: AWS EC2 (Dockerized Infrastructure)

Region: Asia Pacific (Mumbai) --- ap-south-1

------------------------------------------------------------------------

# 📑 TABLE OF CONTENTS

1.  Executive Summary\
2.  Problem Statement\
3.  High-Level Architecture\
4.  System Architecture Diagram\
5.  Agentic Workflow Diagram\
6.  MCP Tooling Architecture\
7.  RAG System Design\
8.  Database Architecture\
9.  Backend Architecture\
10. Frontend Architecture\
11. RBAC & Multi-Tenancy\
12. LLM Cost Governance\
13. Security Architecture\
14. Tech Stack (Versions Included)\
15. Docker & AWS Deployment\
16. Environment Configuration\
17. Project Structure\
18. Local Development Setup\
19. End-to-End Evaluation Flow\
20. Admin & Platform Controls\
21. Engineering Trade-offs\
22. Future Improvements\
23. License & Disclaimer

------------------------------------------------------------------------

# 🎯 Executive Summary

The Agentic Supplier Risk Intelligence System is a production-grade AI
SaaS platform that automates international supplier due diligence.

Traditional supplier verification takes 2--3 days of manual compliance
review.\
This system reduces that to approximately 10 minutes using:

• 5 Specialized AI Agents\
• LangGraph Orchestration\
• Retrieval-Augmented Generation (RAG)\
• Real Sanctions & Registry Data\
• Structured Risk Reporting\
• Full LLM Cost Tracking\
• Multi-Tenant RBAC

------------------------------------------------------------------------

# ❗ Problem Statement

Businesses engaging in international trade must verify:

• Company legitimacy\
• Regulatory compliance\
• Financial consistency\
• Sanctions exposure\
• Public reputation

Manual review is expensive, slow, and error-prone.

This system automates the entire lifecycle with explainable AI
reasoning.

------------------------------------------------------------------------

# 🏗 High-Level Architecture

Frontend (React + Vite + Tailwind)\
↓\
FastAPI Backend (Docker on EC2)\
↓\
PostgreSQL \| Redis \| Qdrant \| MinIO

------------------------------------------------------------------------

# 🧩 System Architecture Diagram

                ┌────────────────────────────┐
                │    React Frontend (S3)     │
                └──────────────┬─────────────┘
                               │ HTTP
                               ▼
                ┌────────────────────────────┐
                │    FastAPI Backend (EC2)   │
                └──────────────┬─────────────┘
                               │
        ┌──────────────┬───────┼────────┬──────────────┐
        ▼              ▼       ▼        ▼              ▼

PostgreSQL Redis Qdrant MinIO LangGraph (Primary DB) (Cache) (Vector)
(Storage) (Orchestration)

------------------------------------------------------------------------

# 🤖 Agentic Workflow Diagram

Planner Agent\
↓\
Document Intelligence Agent\
↓\
RAG Knowledge Agent\
↓\
External Intelligence Agent\
↓\
Decision & Report Agent\
↓\
Final Risk Assessment Stored in Database

------------------------------------------------------------------------

# 🛠 MCP Tooling Architecture

MCP separates reasoning from execution.

Agent decides WHY.\
Tool defines HOW.

Tool Groups:

MCP-1 → Document Tools\
MCP-2 → News Intelligence\
MCP-3 → Company Registry\
MCP-4 → Sanctions & Watchlists

------------------------------------------------------------------------

# 📚 RAG System Design

4 Compliance PDFs\
↓\
Chunking (\~700 tokens)\
↓\
HuggingFace all-mpnet-base-v2 (768-dim)\
↓\
Qdrant Vector Store\
↓\
Top-5 Semantic Retrieval\
↓\
LLM Synthesis with Citations

Indexed Chunks: 619

------------------------------------------------------------------------

# 🗄 Database Architecture

PostgreSQL (9 Tables) • companies\
• users\
• suppliers\
• evaluations\
• documents\
• rag_documents\
• api_keys\
• notifications\
• usage_tracking

Redis • Rate limiting\
• JWT blacklist\
• RAG caching

Qdrant • Vector DB (768-dim embeddings)

MinIO • S3-compatible object storage

------------------------------------------------------------------------

# 🧱 Backend Architecture

FastAPI\
• JWT Authentication\
• RBAC Middleware\
• Redis Rate Limiter\
• Centralized LLMService\
• LangGraph Orchestration\
• Celery Background Tasks

------------------------------------------------------------------------

# 🖥 Frontend Architecture

React 18\
Vite\
Tailwind CSS\
shadcn/ui\
TanStack Query\
Recharts\
Framer Motion

10 Fully Implemented SaaS Pages.

------------------------------------------------------------------------

# 🔐 RBAC & Multi-Tenant Design

Roles:

super_admin → Platform Owner\
admin → Company Owner\
analyst → Create Evaluations\
viewer → Read-only

Super Admin is created manually in database (never via signup).

------------------------------------------------------------------------

# 💰 LLM Cost Governance

All OpenAI calls routed via LLMService.

Tracks: • Prompt tokens\
• Completion tokens\
• Total tokens\
• Total cost\
• Agent name\
• Evaluation ID\
• Company ID

Stored in usage_tracking table.

------------------------------------------------------------------------

# 🔒 Security Architecture

• JWT Authentication\
• Redis Token Blacklisting\
• bcrypt Password Hashing\
• Rate Limiting\
• Subscription Enforcement\
• Docker Network Isolation\
• Databases not publicly exposed

------------------------------------------------------------------------

# 🧰 Tech Stack

Python 3.10\
FastAPI 0.115.6\
PostgreSQL 15\
Redis 7\
Qdrant Latest\
LangGraph 0.2.52\
HuggingFace 3.3.1\
OpenAI GPT-4o-mini\
Docker 29.2.0\
React 18

------------------------------------------------------------------------

# 🐳 Docker & AWS Deployment

EC2 (m7i-flex.large)\
Docker Compose\
Internal bridge network\
All services containerized

Frontend deployed on AWS S3 static hosting.

------------------------------------------------------------------------

# ⚙ Environment Variables Example

DATABASE_URL=postgresql://user:pass@postgres:5432/db\
REDIS_URL=redis://:password@redis:6379\
QDRANT_HOST=qdrant\
MINIO_ENDPOINT=minio:9000\
ENVIRONMENT=production

------------------------------------------------------------------------

# 📁 Project Structure

AGENTIC_SUPPLIER_RISK_AI/ ├── agents/ ├── api/ ├── data/ ├── mcp_tools/
├── rag/ ├── workflows/ ├── frontend/ ├── docker-compose.yml ├──
requirements.txt └── README.md

------------------------------------------------------------------------

# 🚀 Local Development

docker-compose up -d\
uvicorn api.main:app --reload\
cd frontend\
npm run dev

------------------------------------------------------------------------

# 🔄 Evaluation Flow

1.  Supplier Created\
2.  Documents Uploaded\
3.  Evaluation Triggered\
4.  5 Agents Execute Sequentially\
5.  Decision Generated\
6.  Stored in DB\
7.  Email Sent\
8.  Cost Logged

------------------------------------------------------------------------

# 📊 Admin & Platform Controls

• Usage Summary\
• Monthly Cost Analytics\
• Company Deactivation\
• Permanent Delete (GDPR)\
• Top Expensive Evaluations

------------------------------------------------------------------------

# ⚖ Engineering Trade-offs

HuggingFace over OpenAI embeddings → Cost optimization\
Qdrant over FAISS → Persistence\
Manual super_admin → Security\
Redis fail-open → Availability

------------------------------------------------------------------------

# 🔮 Future Improvements

• HTTPS via Nginx\
• CloudFront CDN\
• CI/CD Pipeline\
• Auto DB Backup\
• Multi-region deployment

------------------------------------------------------------------------

# 📜 License & Disclaimer

Portfolio Engineering Project.\
Provides decision-support only.\
Not a legal compliance authority.

------------------------------------------------------------------------

Author: Mohamed Sahad M\
AI Systems Engineer
