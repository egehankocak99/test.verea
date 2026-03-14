# Verea Integration Service

Small Python service that fetches HubSpot contacts and exposes them through a clean internal API at `GET /contacts`. OAuth2 token handling is isolated behind a Nango adapter, so the rest of the codebase never handles raw tokens directly.

## Setup and Run

Prerequisites:
- Python 3.10+
- pip

Clone the repository:

```bash
git clone https://github.com/egehankocak99/test.verea.git
cd test.verea
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Mac/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the local environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Mac/Linux:

```bash
cp .env.example .env
```

Run the service:

```bash
uvicorn app.main:app --reload
```

Open these URLs:
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

Local behavior with the default mock setup:
- `GET /health` returns `200` with `{"status": "ok"}`
- `GET /contacts` returns `401` with `{"detail": "HubSpot token is expired or invalid."}` because `USE_MOCK_TOKEN=true` returns a fake token intentionally

Run the tests:

```bash
pytest tests/ -v
```

Verified result:

```text
21 passed in 0.25s
```

## Architecture Note

The service is split into clear layers: `router.py` handles HTTP, `service.py` orchestrates token retrieval and contact fetching, `repository.py` talks to HubSpot and normalises raw payloads, and `nango/client.py` handles token retrieval only. The main design pattern used is the Adapter pattern in the token layer through `TokenProvider`, `MockTokenProvider`, and `NangoTokenProvider`. Light DDD thinking is applied by separating raw HubSpot responses from the internal `Contact` entity.

## Tradeoffs

This version uses a mock token provider by default, so the integration boundary is demonstrated without requiring a live Nango account. The current implementation fetches a single page of contacts, does not retry on rate limits, does not cache responses, and does not add authentication to the internal API. With more time, I would add pagination, retry with backoff, caching, internal API auth, and live Nango wiring.

## AI Usage Log

I used an AI coding assistant in VS Code for scaffolding, repository logic, router generation, and pytest file generation, then reviewed and adjusted the output manually.

One example prompt was to generate the three pytest files for normalisation, repository behavior, and router contract testing in one pass.

One generated issue was a stray file-creation line left inside `test_repository.py`, which caused a syntax error during collection. I removed that line and kept `test_router.py` as a separate file.

Another issue appeared when `tests/test_repository.py::test_fetch_contacts_skips_malformed_contact` failed because `None.get()` raised `AttributeError`. I updated the repository exception handling to skip that malformed contact correctly.

## Note on Commit History

I completed the implementation in step-sized parts, but I did not create commits at the exact moment each step was finished. Before submission, I reconstructed the history into the same logical steps with descriptive commit messages so the development flow remains easy to review.