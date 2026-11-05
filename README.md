# Mock Interview System

Enterprise-grade, low-latency AI mock interview platform utilizing multi-agent state orchestration and voice interaction.

## Architecture

- **Frontend**: Next.js (App Router), Tailwind CSS, Web Audio API, Framer Motion
- **Backend**: FastAPI (Python 3.11+), LangGraph, LangSmith
- **Database**: PostgreSQL (Session state checkpointer via `PostgresSaver`, user evaluation records)
- **AI / LLM**: Google Gemini 2.0 Flash
- **Voice Pipeline**: Web Audio API (STT/TTS streaming) with future adapter for Sarvam AI

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
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Template for environment configuration
├── frontend/                # Next.js application (client interface)
├── .gitignore
└── README.md
```

## Setup and Development

Detailed setup instructions will be updated incrementally as each module is built and validated.
