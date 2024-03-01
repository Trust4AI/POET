from enum import Enum

from pydantic import BaseModel, constr, conlist
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator

from . import validators


class TemplateCreate(BaseModel):
    base: constr(min_length=1 ,max_length=255)
    description: constr(min_length=1 ,max_length=255)

    class Config:
        from_attributes = True


class TemplateRetrieve(BaseModel):
    id: int
    base: constr(min_length=1 ,max_length=255)
    description: constr(min_length=1 ,max_length=255)
    base_markers: list['BaseMarkerRetrieve']
    composite_markes: list['CompositeMarkerRetrieve']

    class Config:
        from_attributes = True


class BaseMarkerCreate(BaseModel):
    name: constr(min_length=1 ,max_length=255)
    description: constr(min_length=1 ,max_length=255)
    options: conlist(str, min_length=1)
    template_id: int

    class Config:
        from_attributes = True

class BaseMarkerRetrieve(BaseModel):
    id: int
    name: str
    description: str
    options: conlist(str, min_length=1)
    template_id: int

    class Config:
        from_attributes = True


class CompositeMarkerCreate(BaseModel):
    options: Annotated[dict[str, list[str]], AfterValidator(validators.validate_options)]
    template_id: int

    class Config:
        from_attributes = True


class CompositeMarkerRetrieve(BaseModel):
    id: int
    options: Annotated[dict[str, list[str]], AfterValidator(validators.validate_options)]
    template_id: int

    class Config:
        from_attributes = True


class Type(str, Enum):
    bias = "bias"
    safety = "safety"


class Input(BaseModel):
    id: int
    query: constr(min_length=1 ,max_length=255)
    type: Annotated[Type, AfterValidator(validators.validate_type)]

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str

