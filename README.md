# Verea Integration Service

Note that alongside my submission, I will be attaching a detailed explanation on my thought process and everything I have done. This is mostly focused on how to run, and the basics.

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

Alternative: run with Docker:

```bash
docker-compose up --build
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

This version uses a mock token provider by default, so the integration boundary is demonstrated without requiring a live Nango account. 

## Moving Forward:

1. Pagination — highest priority.
Add a cursor loop in `repository.py` that follows HubSpot's `paging.next.after` 
field until there are no more pages. The interface to the rest of the app 
stays identical — `fetch_contacts()` still returns a flat list — the loop 
is entirely internal to the repository.

2. Retry with exponential backoff on 429.
Wrap the HubSpot call in a retry decorator that reads the `Retry-After` 
header from the 429 response and waits that many seconds before retrying, 
up to a configurable maximum number of attempts. After that it raises as 
it does today.

3. Response caching with a TTL.
Add a simple in-memory cache on `fetch_contacts()` with a 60 second TTL. 
For a more production-grade setup, replace the in-memory cache with Redis 
so the cache survives service restarts and works across multiple instances.

4. API key authentication middleware.
Add a FastAPI middleware that checks for a valid API key in the 
`X-API-Key` header on every request. Keys stored in environment variables, 
checked before the request reaches any endpoint.

5. Real Nango connection.
Register a Nango account, create a HubSpot OAuth2 integration, store the 
connection ID in `.env`, and flip `USE_MOCK_TOKEN=false`. The 
`NangoTokenProvider` class is already implemented — this is purely a 
credentials and configuration step, no code changes needed.

6. Structured logging.
Add Python's standard `logging` module configured to output JSON-formatted 
log lines. Log every incoming request, every outbound HubSpot call with its 
response time, and every error with full context. This makes the service 
debuggable in production without needing to reproduce issues locally.

7. docker-compose.yml.
A single `docker-compose.yml` that builds the service image and runs it 
with the correct environment variables. One command to go from a fresh 
clone to a running service — removes all manual setup steps from the 
README.

8. Contact field validation.*
Add an email format validator to the Contact model using Pydantic's 
`EmailStr` type. Add a separate validation step in the repository that 
flags contacts with both empty name and empty email as suspect rather than 
passing them through silently.


## Note on Commit History

I completed the implementation in step-sized parts, but I did not create commits at the exact moment each step was finished. Before submission, I reconstructed the history into the same logical steps with descriptive commit messages so the development flow remains easy to review. Readme file was also committed at last. 

Docker Update: 

I also added a `Dockerfile` and `docker-compose.yml` for easier local setup and testing. This Docker setup was written manually.