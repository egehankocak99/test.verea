from fastapi import APIRouter, HTTPException

from app.contacts.models import Contact
from app.contacts.service import get_contacts


router = APIRouter()


@router.get("/contacts", response_model=list[Contact])
def contacts_endpoint():
	"""
	GET /contacts
	Returns a normalised list of contacts from HubSpot.
	Each contact has: id, name, email, source.
	"""
	try:
		return get_contacts()

	except PermissionError as e:
		# token expired or missing
		raise HTTPException(status_code=401, detail=str(e))

	except RuntimeError as e:
		# rate limit or unexpected HubSpot status
		raise HTTPException(status_code=502, detail=str(e))

	except ConnectionError as e:
		# could not reach HubSpot at all
		raise HTTPException(status_code=503, detail=str(e))

	except Exception as e:
		# catch-all for anything unexpected
		raise HTTPException(status_code=500, detail="An unexpected error occurred.")