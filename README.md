# Verea Integration Engineer Take-Home

## Setup

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and adjust values if needed.
4. Run the service with Uvicorn.

Example commands on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The service starts with a health endpoint at `/health`.

## Architecture Notes

This project uses a layered structure: API in `app/main.py` and `app/contacts/router.py`, domain logic in `app/contacts`, and integration concerns in `app/nango`. The `TokenProvider` abstraction is the first part of an Adapter pattern so the rest of the code does not depend on Nango directly.

## Tradeoffs

This scaffold sets up the project structure first. The HubSpot client, contact normalisation, error mapping, and endpoint tests are intentionally left for the next implementation step.

## AI Usage Log

To be completed as the exercise progresses.