# ResearchPilot AI 🚀

> An intelligent, AI-powered agentic platform designed to accelerate academic literature discovery, semantic analysis, and synthesis.

ResearchPilot AI is a comprehensive web application designed to help researchers organize, explore, and analyze academic papers. It integrates advanced Large Language Model (LLM) agents, local document parsing, semantic vector search, and direct academic repository integrations to streamline the literature review process.

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Screenshots & UI Showcase](#-screenshots--ui-showcase)
- [Installation & Setup](#-installation--setup)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Configuration](#-environment-configuration)
- [Future Scope](#-future-scope)
- [License](#-license)

---

## 🌟 Project Overview

Academic literature research can be overwhelming, with thousands of publications released daily across various fields. ResearchPilot AI addresses this challenge by providing researchers with a personal hub to:
1. **Discover**: Search major academic databases (NeurIPS, ICML, ICLR, Semantic Scholar, etc.) and import metadata and access links with one click.
2. **Organize**: Group literature into independent, context-specific Workspaces.
3. **Parse & Store**: Upload PDFs, automatically parse text, and index documents using semantic vector stores.
4. **Synthesize & Chat**: Converse with a workspace-aware AI assistant that can cite specific parts of uploaded papers, and run automated analysis tasks (like summarizations, comparative matrices, or critical reviews).

---

## ✨ Key Features

### 📁 Smart Workspaces
Create independent, sandboxed environments for different research projects or topics. Each workspace maintains its own collection of papers, vector index, and active chat threads.

### 🔍 Academic Paper Discovery
* Integration with academic search engines.
* Real-time metadata importing.
* Full-text PDF download links and open-access URL tracking.

### 📄 Local PDF Processing & RAG
* Automated PDF extraction and parsing using `pypdf`.
* Text chunking and embedding generation using local sentence transformers (`all-MiniLM-L6-v2`).
* Semantic storage in a high-performance local Chroma DB instance for fast document lookup and context retrieval.

### 💬 Workspace-Aware AI Chat
* Interactive chat interface with historical memory.
* RAG-powered answers with precise citations from the uploaded documents.
* Multi-LLM provider support (Groq, Gemini, OpenRouter, and Ollama) with self-testing capabilities on startup.

### 🤖 Multi-Agent AI Research Tools
* **Paper Summarizer**: Extracts key contributions, methodology, and results in a structured format.
* **Insights Generator**: Identifies non-obvious patterns, implications, and practical takeaways.
* **Research Paper Reviewer**: Formulates a critical academic review assessing strengths, weaknesses, and potential biases.
* **Literature Reviewer**: Synthesizes multiple papers to outline common themes, agreements, and debates.
* **Paper Comparison**: Generates a side-by-side comparison matrix of selected publications.

### 🔐 Security & User Management
* Safe user registration and login with JWT token authentication.
* Secure email verification and password recovery using One-Time Passcodes (OTP).

---

## 🏗️ Tech Stack

### Frontend
* **Core**: React 19 (TypeScript), Vite 8
* **Routing**: React Router DOM 7
* **Styling**: Tailwind CSS 3 (utility-first, responsive grid, glassmorphism overlays)
* **Icons & UI Assets**: Lucide React
* **API Client**: Axios with request/response interceptors for automatic JWT authentication headers

### Backend
* **Core**: FastAPI (Python 3.9+)
* **Server**: Uvicorn (ASGI web server)
* **Database (SQL)**: SQLite / SQLAlchemy (auto-migrating relational models)
* **Vector Store**: Chroma DB (vector database for document embeddings)
* **Embeddings Model**: local Sentence-Transformers (`all-MiniLM-L6-v2`)
* **Parsing**: `pypdf` for extracting text from uploaded PDFs

### Supported LLM APIs
* **Groq** (Primary provider for ultra-fast `llama-3.3-70b-versatile`)
* **Google Gemini** (`gemini-1.5-flash`)
* **OpenRouter** (`meta-llama/llama-3.1-8b-instruct:free` or any preferred models)
* **Ollama** (Support for local execution of models like `llama3.1`)

---

## 📸 Screenshots & UI Showcase

*Below are placeholders showing the primary application dashboards and workflows:*

#### 🖥️ Main Dashboard
*A summary view showing recent activity, active workspaces, and core research metrics.*
`![Dashboard Placeholder](docs/screenshots/dashboard.png)`

#### 💬 Workspace Chat
*Conversing with the RAG-enabled AI agent about imported papers.*
`![Workspace Chat Placeholder](docs/screenshots/workspace_chat.png)`

#### 🔍 Paper Discovery & Search
*Searching and importing papers from Semantic Scholar, NeurIPS, and other databases.*
`![Paper Discovery Placeholder](docs/screenshots/paper_discovery.png)`

#### 🛠️ AI Research Tools Panel
*Running structured analyses, such as paper summaries and comparison matrices.*
`![AI Research Tools Placeholder](docs/screenshots/ai_tools.png)`

---

## ⚙️ Installation & Setup

### Prerequisites
Before setting up the project, make sure you have the following installed:
* **Node.js** (v18 or higher)
* **Python** (v3.9 or higher)
* **Git** (for version control)

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   * **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your environment variables:**
   * Copy the template configuration file:
     ```bash
     cp .env.example .env
     ```
   * Open the new `.env` file and input your credentials, API keys (Groq, Gemini, etc.), and SMTP mail configuration.
   * If you do not have a Groq or Gemini API key, leave them empty to run the backend in a simulated **Mock Mode** for offline testing.

5. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
   ```
   *The backend server will run on `http://127.0.0.1:8001`.*

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Install the Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the Vite development server:**
   ```bash
   npm run dev
   ```
   *The frontend application will start on `http://localhost:5173` (or the port specified in the console).*

---

## 🔒 Environment Configuration

The application backend reads variables from `.env`. A complete configuration includes:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `JWT_SECRET` | Secret key used for signing authentication tokens. | `your_jwt_secret_key` |
| `DATABASE_URL` | SQLAlchemy database URL. | `sqlite:///./research_pilot.db` |
| `CHROMA_DB_PATH` | Directory where Chroma DB indexes are stored. | `data/chroma_db` |
| `UPLOAD_DIR` | Directory where uploaded PDFs are stored locally. | `data/uploads` |
| `GROQ_API_KEY` | Groq API Key to enable high-speed LLM processing. | `gsk_...` |
| `GEMINI_API_KEY` | Google Gemini API Key. | `AIzaSy...` |
| `OPENROUTER_API_KEY` | OpenRouter API Key for server access to other models. | `sk-or-v1-...` |
| `OLLAMA_BASE_URL` | API endpoint for local Ollama server if running. | `http://localhost:11434` |
| `SMTP_HOST` | Host address of your SMTP server (for sending OTPs). | `smtp.gmail.com` |
| `SMTP_USERNAME` | Username of your SMTP email account. | `your-email@gmail.com` |
| `SMTP_PASSWORD` | App password for SMTP account. | `your-app-password` |

*Refer to `backend/.env.example` for the complete setup template.*

---

## 🚀 Future Scope

* **Multi-User Collaboration**: Live shared workspaces with real-time updates and group chats.
* **Interactive PDF Annotator**: View PDFs directly in the application with sticky notes, highlights, and custom tags mapped to LLM notes.
* **Deep Semantic Mapping**: Generate an interactive 2D/3D knowledge graph of all imported papers, showing citation links and semantic similarity clusters.
* **Agentic Literature Search**: Autonomous research agents that scrape the web, fetch related papers, analyze citation trees, and generate complete drafts of state-of-the-art reports.
* **Citation Exports**: Instant generation and downloading of citations in BibTeX, APA, MLA, or Chicago formats.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
