# Mock Interview System

Enterprise-grade AI mock interview platform utilizing multi-agent state orchestration and voice interaction. Built entirely with Python.

## Architecture

- **Frontend (UI)**: Streamlit (Pure Python client with audio recording, PDF upload, and evaluation dashboard)
- **Backend (API & Engine)**: FastAPI, LangGraph, LangSmith
- **Database**: PostgreSQL (Session state checkpointer via `PostgresSaver`, interview records)
- **AI / LLM**: Google Gemini 2.0 Flash
- **Voice Pipeline**: Audio capture & synthesis with adapter for Sarvam AI / Gemini Audio

## Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Configuration and database settings
│   │   ├── graph/           # LangGraph state machine, nodes, and router logic
│   │   ├── schemas/         # Pydantic schemas for validation
│   │   ├── services/        # PDF extraction, LLM clients, audio utilities
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # Unit and integration test suites
│   ├── requirements.txt     # Python backend dependencies
│   └── .env.example         # Template for environment configuration
├── frontend/
│   ├── app.py               # Streamlit application entrypoint
│   ├── components/          # Reusable UI widgets (recording, transcript, metrics)
│   └── requirements.txt     # Streamlit frontend dependencies
├── .gitignore
└── README.md
```

## Setup and Development

All components run on Python 3.11+. No Node.js runtime required.
