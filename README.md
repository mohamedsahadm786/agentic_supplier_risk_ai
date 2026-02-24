# 🧠 Agentic Supplier Risk Intelligence System

### Production-Grade Multi-Tenant AI SaaS for Automated Supplier Risk Evaluation

------------------------------------------------------------------------

## 🌍 Live Deployment

**Frontend (AWS S3 Static Hosting):**\
http://agentic-supplier-risk-frontend-786.s3-website.ap-south-1.amazonaws.com/platform-admin

**Backend:** AWS EC2 (Dockerized Infrastructure)\
**Region:** Asia Pacific (Mumbai) --- ap-south-1

------------------------------------------------------------------------

# 📑 Table of Contents

-   [Executive Summary](#executive-summary)
-   [Business Problem & Motivation](#business-problem--motivation)
-   [System Vision & Objectives](#system-vision--objectives)
-   [High-Level Architecture](#high-level-architecture)
-   [Complete Infrastructure Diagram](#complete-infrastructure-diagram)
-   [Agentic Workflow Orchestration](#agentic-workflow-orchestration)
-   [Detailed Agent Architecture](#detailed-agent-architecture)
-   [MCP Tooling Layer (Model Context
    Protocol)](#mcp-tooling-layer-model-context-protocol)
-   [RAG System Architecture](#rag-system-architecture)
-   [Database Architecture (4
    Databases)](#database-architecture-4-databases)
-   [Backend Architecture (FastAPI
    Layer)](#backend-architecture-fastapi-layer)
-   [Frontend Architecture (React SaaS
    UI)](#frontend-architecture-react-saas-ui)
-   [Multi-Tenant RBAC Design](#multi-tenant-rbac-design)
-   [LLM Cost Governance &
    Observability](#llm-cost-governance--observability)
-   [Security Architecture](#security-architecture)
-   [Technology Stack (With Versions)](#technology-stack-with-versions)
-   [Docker & Containerization
    Strategy](#docker--containerization-strategy)
-   [AWS Production Deployment](#aws-production-deployment)
-   [Environment Configuration](#environment-configuration)
-   [Project Structure](#project-structure)
-   [Local Development Setup](#local-development-setup)
-   [End-to-End Evaluation Lifecycle](#end-to-end-evaluation-lifecycle)
-   [Admin Analytics & Platform
    Controls](#admin-analytics--platform-controls)
-   [Engineering Trade-offs & Design
    Decisions](#engineering-trade-offs--design-decisions)
-   [Future Improvements & Roadmap](#future-improvements--roadmap)
-   [License & Disclaimer](#license--disclaimer)

------------------------------------------------------------------------

# Executive Summary

The **Agentic Supplier Risk Intelligence System** is a production-grade,
multi-tenant AI SaaS platform designed to automate international
supplier due diligence.

Traditional supplier verification can take **2--3 days** of manual
compliance review.\
This system reduces the process to **\~10 minutes** using:

-   5 Specialized AI Agents\
-   LangGraph State Machine Orchestration\
-   Retrieval-Augmented Generation (RAG)\
-   Real Government Sanctions Data\
-   Live Registry & News Intelligence\
-   Structured Risk Assessment Reports\
-   Full LLM Cost Tracking & Governance\
-   Enterprise-Ready RBAC

This is not a prototype --- it is architected as a **real SaaS
product**.

------------------------------------------------------------------------

# Business Problem & Motivation

Global trade involves serious risks:

-   Fraudulent suppliers\
-   Sanctioned entities\
-   Fake export licenses\
-   Financial inconsistencies\
-   Regulatory non-compliance

Compliance teams manually:

-   Review PDFs\
-   Cross-check registries\
-   Search news reports\
-   Verify sanctions\
-   Confirm export compliance

This process is expensive, slow, and error-prone.

This platform automates the full lifecycle with explainable AI reasoning
and audit trails.

------------------------------------------------------------------------

# System Vision & Objectives

-   Build a production-ready AI SaaS platform
-   Implement real-world multi-tenant architecture
-   Track and govern AI costs
-   Provide explainable risk reasoning
-   Maintain enterprise-grade security
-   Demonstrate senior-level systems engineering

------------------------------------------------------------------------

# High-Level Architecture

    React Frontend (S3 Hosted)
            │
            ▼
    FastAPI Backend (EC2 Docker)
            │
            ├── PostgreSQL (Primary DB)
            ├── Redis (Rate Limiting + JWT Blacklist)
            ├── Qdrant (Vector Database for RAG)
            ├── MinIO (Document Storage)
            └── LangGraph (Agent Orchestration Engine)

------------------------------------------------------------------------

# Complete Infrastructure Diagram

                               ┌──────────────────────────┐
                               │     React Frontend       │
                               │   (AWS S3 Static Site)   │
                               └─────────────┬────────────┘
                                             │ HTTPS
                                             ▼
                               ┌──────────────────────────┐
                               │     FastAPI Backend      │
                               │      (EC2 + Docker)      │
                               └─────────────┬────────────┘
                                             │
             ┌───────────────┬───────────────┼───────────────┬──────────────┐
             ▼               ▼               ▼               ▼              ▼
      PostgreSQL         Redis            Qdrant          MinIO        LangGraph
     (Relational DB)   (Cache + Auth)   (Vector DB)   (Object Store) (State Engine)

------------------------------------------------------------------------

# Agentic Workflow Orchestration

    Planner Agent
          ↓
    Document Intelligence Agent
          ↓
    RAG Knowledge Agent
          ↓
    External Intelligence Agent
          ↓
    Decision & Report Agent
          ↓
    Final Risk Assessment Stored in PostgreSQL

Executed via LangGraph sequential state machine.

------------------------------------------------------------------------

# Detailed Agent Architecture

### 1️⃣ Planner Agent

-   Task decomposition
-   No tool usage
-   Structured JSON output

### 2️⃣ Document Intelligence Agent

-   Extracts data from PDFs
-   Detects inconsistencies
-   Flags missing documents

### 3️⃣ RAG Knowledge Agent

-   Retrieves internal compliance policies
-   Uses 768-dim embeddings
-   Provides citations & confidence

### 4️⃣ External Intelligence Agent

-   UK Companies House
-   NewsAPI
-   EU Sanctions
-   OFAC Sanctions
-   UN Sanctions

### 5️⃣ Decision Agent

-   Synthesizes all signals
-   Outputs structured risk report

------------------------------------------------------------------------

# MCP Tooling Layer (Model Context Protocol)

MCP separates reasoning from execution.

  MCP Group   Purpose
  ----------- ------------------------
  MCP-1       Document Tools
  MCP-2       News Intelligence
  MCP-3       Company Registry
  MCP-4       Sanctions & Watchlists

------------------------------------------------------------------------

# RAG System Architecture

    4 Compliance PDFs
          ↓
    Text Extraction
          ↓
    Chunking (~700 tokens)
          ↓
    HuggingFace all-mpnet-base-v2
          ↓
    768-dim Embeddings
          ↓
    Qdrant Collection: compliance_policies
          ↓
    Top-5 Retrieval
          ↓
    LLM Response with Citations

Indexed Chunks: **619**

------------------------------------------------------------------------

# Database Architecture (4 Databases)

## PostgreSQL

9 Tables: - companies - users - suppliers - evaluations - documents -
rag_documents - api_keys - notifications - usage_tracking

## Redis

-   Rate limiting
-   JWT blacklisting
-   RAG caching

## Qdrant

-   Vector database
-   Cosine similarity search

## MinIO

-   Stores uploaded supplier documents

------------------------------------------------------------------------

# Backend Architecture (FastAPI Layer)

-   JWT Authentication
-   Role-Based Middleware
-   Redis Rate Limiter
-   Centralized LLMService
-   Celery Background Execution
-   LangGraph Workflow Engine

------------------------------------------------------------------------

# Frontend Architecture (React SaaS UI)

-   React 18
-   Vite
-   Tailwind CSS
-   shadcn/ui
-   TanStack Query
-   Recharts
-   Framer Motion

10 Fully Implemented SaaS Pages.

------------------------------------------------------------------------

# Multi-Tenant RBAC Design

  Role          Scope
  ------------- --------------------
  super_admin   Platform Owner
  admin         Company Owner
  analyst       Create Evaluations
  viewer        Read Only

Super Admin created manually in database.

------------------------------------------------------------------------

# LLM Cost Governance & Observability

Centralized LLMService tracks:

-   Prompt tokens
-   Completion tokens
-   Total tokens
-   Cost per call
-   Agent name
-   Evaluation ID
-   Company ID

Stored in `usage_tracking` table.

------------------------------------------------------------------------

# Security Architecture

-   JWT Authentication
-   Redis Token Blacklisting
-   bcrypt Password Hashing
-   Rate Limiting
-   Subscription Enforcement
-   Docker Network Isolation
-   Databases not publicly exposed

------------------------------------------------------------------------

# Technology Stack (With Versions)

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

# Docker & Containerization Strategy

-   Full Docker Compose deployment
-   Internal bridge networking
-   No localhost dependencies
-   Environment-driven configuration
-   Restart policies enabled

------------------------------------------------------------------------

# AWS Production Deployment

Backend: - EC2 (m7i-flex.large) - Docker Compose

Frontend: - AWS S3 Static Hosting

Security Groups: - 8000 open - Databases restricted

------------------------------------------------------------------------

# Environment Configuration

Example:

DATABASE_URL=postgresql://user:pass@postgres:5432/db\
REDIS_URL=redis://:password@redis:6379\
QDRANT_HOST=qdrant\
MINIO_ENDPOINT=minio:9000

------------------------------------------------------------------------

# Project Structure

AGENTIC_SUPPLIER_RISK_AI/ ├── agents/ ├── api/ ├── data/ ├── mcp_tools/
├── rag/ ├── workflows/ ├── frontend/ ├── docker-compose.yml ├──
requirements.txt └── README.md

------------------------------------------------------------------------

# Local Development Setup

docker-compose up -d\
uvicorn api.main:app --reload\
cd frontend\
npm run dev

------------------------------------------------------------------------

# End-to-End Evaluation Lifecycle

1.  Supplier Created\
2.  Documents Uploaded\
3.  Evaluation Triggered\
4.  Agents Execute Sequentially\
5.  Decision Generated\
6.  Stored in DB\
7.  Email Sent\
8.  Cost Logged

------------------------------------------------------------------------

# Admin Analytics & Platform Controls

-   Usage Summary
-   Monthly Cost Trends
-   Company Deactivation
-   GDPR Permanent Delete
-   Top Expensive Evaluations

------------------------------------------------------------------------

# Engineering Trade-offs & Design Decisions

-   HuggingFace over OpenAI embeddings → Cost optimization
-   Qdrant over FAISS → Persistence
-   Manual super_admin creation → Security
-   Redis fail-open → Availability

------------------------------------------------------------------------

# Future Improvements & Roadmap

-   HTTPS via Nginx
-   CloudFront CDN
-   CI/CD pipeline
-   Automated backups
-   Multi-region support

------------------------------------------------------------------------

# License & Disclaimer

Portfolio Engineering Project.\
Provides decision-support only.\
Not a legal compliance authority.

------------------------------------------------------------------------

Author: Mohamed Sahad M\
AI Systems Engineer
