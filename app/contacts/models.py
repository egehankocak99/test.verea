from pydantic import BaseModel


class Contact(BaseModel):
    id: str
    name: str
    email: str
    source: str