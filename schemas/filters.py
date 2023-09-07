from pydantic import BaseModel, UUID4


class destination(BaseModel):
    id: UUID4
    country: str
    city: str
