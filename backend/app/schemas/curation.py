from uuid import UUID

from pydantic import BaseModel


class ColorMappingRead(BaseModel):
    element: str
    color_name: str
    hex_code: str | None

    model_config = {"from_attributes": True}


class CurationItemRead(BaseModel):
    id: UUID
    element: str
    name: str
    category: str
    image_url: str

    model_config = {"from_attributes": True}


class CurationResponse(BaseModel):
    missing_elements: list[str]
    colors: list[ColorMappingRead]
    items: list[CurationItemRead]
    locked: bool
