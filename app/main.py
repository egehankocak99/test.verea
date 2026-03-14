from fastapi import FastAPI

from app.contacts.router import router as contacts_router


app = FastAPI(
    title="Verea Integration Service",
    description="Fetches and normalises contacts from HubSpot via Nango",
    version="1.0.0"
)

app.include_router(contacts_router)


@app.get("/health")
def health():
    return {"status": "ok"}