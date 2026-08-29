# 🩺 HIA (Health Insights Agent)

AI Agent to analyze blood reports and provide detailed health insights.

## 🌟 Features

- **Agent-based architecture**
  - **Analysis Agent**: Report analysis with in-context learning from previous analyses and a built-in knowledge base
    - **Specialist analysis modes**: choose a Comprehensive read of your report, or a focused **Cardiac**, **Endocrine & Metabolic**, or **Nutrition** lens, each with its own tailored prompt and recommendations
  - **Chat Agent**: RAG-powered follow-up Q&A over your report (FAISS + HuggingFace embeddings)
- **Multi-model cascade** via Groq with automatic fallback (primary → secondary → tertiary → fallback)
  - **Cascade transparency**: a sidebar panel shows all four model tiers and how many times each has been used this session
  - **Speed/quality preference**: pick Auto, Fastest, Balanced, or Most Powerful to control which tier a new analysis starts from
- **Chat sessions**: Create multiple analysis sessions; each session stores report, analysis, and follow-up messages in Supabase
- **Report sources**: Upload your own PDF or use the built-in sample report for quick testing
- **PDF handling**: Upload up to 20MB, max 50 pages; validation for file type and medical-report content
- **Daily analysis limit**: Configurable cap (default 15/day) with a visual progress indicator in the sidebar
- **Secure auth**: Supabase Auth (sign up / sign in), session validation, and configurable session timeout
- **Session history**: View, switch, and delete past sessions; report text persisted for follow-up chat across reloads
- **Modern, uniform UI**: A shared theme (`src/config/theme.py`) applies one consistent design system — cards, badges, buttons, and chat bubbles — across the login screen, sidebar, forms, and chat, instead of ad-hoc per-screen styling

## 🛠️ Tech Stack

- **Frontend**: Streamlit (1.42+)
- **AI / LLM**
  - **Report analysis**: Groq with multi-model fallback via `ModelManager`, selectable per-analysis starting tier (Auto/Fastest/Balanced/Most Powerful)
    - Primary: `openai/gpt-oss-120b`
    - Secondary: `openai/gpt-oss-20b`
    - Tertiary: `qwen/qwen3.6-27b`
    - Fallback: `groq/compound-mini`
  - **Specialist prompts**: Comprehensive, Cardiac, Endocrine & Metabolic, and Nutrition analysis modes (`config/prompts.py`)
  - **Follow-up chat**: RAG with LangChain, HuggingFace embeddings (`all-MiniLM-L6-v2`), FAISS vector store, and Groq (`openai/gpt-oss-120b`)
- **Database**: Supabase (PostgreSQL)
  - Tables: `users`, `chat_sessions`, `chat_messages`
- **Auth**: Supabase Auth, Gotrue
- **PDF**: PDFPlumber (text extraction), filetype (file validation)
- **Libraries**: LangChain, LangChain Community, LangChain HuggingFace, LangChain Text Splitters, sentence-transformers, FAISS (CPU)

## 🚀 Installation

#### Requirements 📋

- Python 3.8+
- Streamlit 1.42+
- Supabase account
- Groq API key
- PDFPlumber, filetype

#### Getting Started 📝

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Required environment variables (in `.streamlit/secrets.toml`):

```toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
GROQ_API_KEY = "your-groq-api-key"
```

3. Set up Supabase database schema:

The application uses three tables: `users`, `chat_sessions`, and `chat_messages`. Use the SQL script at `public/db/script.sql` to create them.



(You can turn off email confirmation on signup in Supabase: **Authentication → Providers → Email → Confirm email**.)

4. Run the application:

```bash
streamlit run src\main.py
```

## 📁 Project Structure

```
hia/
├── requirements.txt
├── README.md
├── src/
│   ├── main.py                 # Application entry point; chat UI and session flow
│   ├── auth/
│   │   ├── auth_service.py     # Supabase auth, sessions, chat message persistence
│   │   └── session_manager.py # Session init, timeout, create/delete chat sessions
│   ├── components/
│   │   ├── analysis_form.py    # Report source (upload/sample), patient form, analysis trigger
│   │   ├── auth_pages.py       # Login / signup pages
│   │   ├── footer.py           # Footer component
│   │   ├── header.py           # User greeting
│   │   └── sidebar.py          # Session list, new session, daily limit, logout
│   ├── config/
│   │   ├── app_config.py       # App name, limits (upload, pages, analysis, timeout)
│   │   ├── prompts.py          # Specialist prompts (Comprehensive, Cardiac, Endocrine, Nutrition)
│   │   ├── sample_data.py      # Sample blood report for "Use Sample PDF"
│   │   └── theme.py            # Shared design system + global CSS injection, used by every screen
│   ├── services/
│   │   └── ai_service.py       # Analysis + chat entry points; vector store caching
│   ├── agents/
│   │   ├── analysis_agent.py   # Report analysis, rate limits, knowledge base, in-context learning
│   │   ├── chat_agent.py       # RAG pipeline (embeddings, FAISS, query contextualization)
│   │   └── model_manager.py   # Groq multi-model cascade and fallback
│   └── utils/
│       ├── validators.py       # Email, password, PDF file and content validation
│       └── pdf_extractor.py   # PDF text extraction and validation
├── public/
│   └── db/
│       ├── script.sql          # Supabase schema (users, chat_sessions, chat_messages)
│       └── schema.png          # Schema diagram
└