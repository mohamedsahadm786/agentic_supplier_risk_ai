# Agentic Supplier Risk Intelligence System

## 🎯 Project Overview

An end-to-end Agentic AI system designed to evaluate supplier onboarding risk using:
- Multi-agent architecture (5 specialized agents)
- RAG (Retrieval Augmented Generation) with local documents
- MCP-style tool interfaces
- LangGraph orchestration

## 🏗️ Architecture

### Agents
1. **Planner Agent** - Breaks business scenarios into tasks
2. **Document Intelligence Agent** - Extracts facts from supplier PDFs
3. **RAG Knowledge Agent** - Queries internal policies using FAISS
4. **External Intelligence Agent** - Checks news, registries, sanctions
5. **Decision & Report Agent** - Produces risk assessment

### Tech Stack
- Python 3.10
- LangGraph (orchestration)
- OpenAI API (LLM + embeddings)
- FAISS (vector store)
- FastAPI (future API layer)

## 📁 Project Structure
```
Agentic_Supplier_Risk_AI/
├── agents/          # AI agent implementations
├── mcp_tools/       # MCP tool interfaces
├── rag/             # RAG pipeline and vector store
├── workflows/       # LangGraph workflows
├── data/            # Documents and external data
├── api/             # FastAPI endpoints (future)
├── config/          # Configuration files
└── tests/           # Unit tests
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- OpenAI API key

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Agentic_Supplier_Risk_AI.git
cd Agentic_Supplier_Risk_AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (once requirements.txt is created)
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OpenAI API key to .env
```

## 📝 Status

**Current Phase**: Project structure setup
- ✅ Folder structure created
- ⏳ Agent implementation (pending)
- ⏳ RAG pipeline (pending)
- ⏳ MCP tools (pending)

## 📄 License

This is a learning/portfolio project.

---

**Note**: This is a decision-support prototype, not a legal authority for supplier risk assessment.
```

5. **Press** → `Ctrl + S` to **save**

---

## **PHASE 2: Initialize Git & Push to GitHub**

### **Step 3: Open Source Control**

1. **Look at the left sidebar** (vertical icon bar)
2. **Click** the **3rd icon from top** (looks like a branch/tree - Source Control)
3. You'll see **"Initialize Repository"** button

---

### **Step 4: Initialize Git**

1. **Click** → **"Initialize Repository"** (blue button)
2. VS Code will ask: **"This will create a Git repository in..."**
3. **Click** → **"Initialize Repository"** (confirm)

✅ Now you'll see all your files listed under **"Changes"**

---

### **Step 5: Stage All Files**

1. **Hover** over **"Changes"** text
2. You'll see a **"+"** icon appear
3. **Click** the **"+"** icon
4. All files move from "Changes" to **"Staged Changes"**

**What this does**: Tells Git "these are the files I want to save"

---

### **Step 6: Commit Files**

1. **Look above** "Staged Changes" - you'll see a text box saying **"Message"**
2. **Click** in that text box
3. **Type**: `Initial project structure with folders and essential files`
4. **Press** → `Ctrl + Enter` (Windows) or `Cmd + Enter` (Mac)

**Alternative**: Click the **✓ checkmark** button above the message box

✅ Files are now committed locally (saved in Git history)

---

### **Step 7: Publish to GitHub**

1. **Look at the top** of the Source Control panel
2. You'll see a button: **"Publish Branch"** or **"Publish to GitHub"**
3. **Click** → **"Publish to GitHub"**

---

### **Step 8: Sign In (if needed)**

If VS Code asks:
1. **Click** → **"Allow"** (to use GitHub)
2. Browser opens → **Sign in** to GitHub
3. **Click** → **"Authorize Visual-Studio-Code"**
4. Return to VS Code

---

### **Step 9: Choose Repository Settings**

VS Code will ask:

**"Publish to GitHub public repository?"**

**Two options appear**:
- 🌍 **Publish to GitHub public repository**
- 🔒 **Publish to GitHub private repository**

**My recommendation**: 
- Choose **public** if this is a portfolio project (recruiters can see it)
- Choose **private** if you want to keep it hidden for now

1. **Click** your choice
2. It will ask for repository name - it suggests `AGENTIC_SUPPLIER_RISK_AI`
3. **Press** → `Enter` (or edit the name if you want)

---

### **Step 10: Wait for Upload**

- VS Code shows progress: **"Publishing..."**
- Takes 5-30 seconds
- Bottom right shows: **"Successfully published"**

✅ **Done!** Your code is on GitHub!

---

## **PHASE 3: Verify Success**

### **Step 11: Open GitHub in Browser**

1. In Source Control panel, **click** the **"..."** (three dots) at top
2. **Click** → **"Remote"** → **"View on GitHub"**

**OR** manually go to:
```
https://github.com/YOUR_USERNAME/AGENTIC_SUPPLIER_RISK_AI