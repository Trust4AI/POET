from enum import Enum
from typing import Optional

from pydantic import BaseModel, constr, conlist
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator

from . import validators


class Template(BaseModel):
    base: constr(min_length=1 ,max_length=255)
    description: constr(min_length=1 ,max_length=255)
    base_markers: list['BaseMarkerRetrieve']
    
    class Config:
        from_attributes = True

    
    def build(self, n: int):
        result = []
        
        for _ in range(n):
            built_string = self.base
            for marker in self.base_markers:
                built_string = marker.replace(built_string)
            result.append(built_string)
        
        return result


    def __repr__(self):
        return f"Template(base={self.base}, description={self.description})"


class TemplateCreate(BaseModel):
    base: constr(min_length=1 ,max_length=255)
    description: constr(min_length=1 ,max_length=255)

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"Template(base={self.base}, description={self.description})"


class TemplateUpdate(BaseModel):
    base: Optional[constr(min_length=1 ,max_length=255)]
    description: Optional[constr(min_length=1 ,max_length=255)]

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"Template(base={self.base}, description={self.description})"


class TemplateRetrieve(BaseModel):
    id: int
    base: constr(min_length=1 ,max_length=255)
    description: constr(min_length=1 ,max_length=255)
    base_markers: list['BaseMarkerRetrieve']
    # composite_markers: list['CompositeMarkerRetrieve']

    class Config:
        from_attributes = True´

    def __repr__(self):
        return f"Template(id={self.id}, base={self.base}, description={self.description})"


class BaseMarker(BaseModel):
    name: constr(min_length=1 ,max_length=255)
    description: constr(min_length=1 ,max_length=255)
    options: list[str]
    template_id: int

    class Config:
        from_attributes = True

    def replace(self, base: str) -> str:
        for option in self.options:
            base = base.replace(self.name, option)
        return base

    def __repr__(self):
        return f"BaseMarker(name={self.name}, description={self.description})"


class BaseMarkerCreate(BaseModel):
    name: constr(min_length=1 ,max_length=255)
    description: constr(min_length=1 ,max_length=255)
    options: conlist(str, min_length=1)
    template_id: int

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"BaseMarker(name={self.name}, description={self.description})"


class BaseMarkerUpdate(BaseModel):
    name: Optional[constr(min_length=1 ,max_length=255)]
    description: Optional[constr(min_length=1 ,max_length=255)]
    options: conlist(str, min_length=1)
    template_id: Optional[int]

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"BaseMarker(name={self.name}, description={self.description})"

class BaseMarkerRetrieve(BaseModel):
    id: int
    name: str
    description: str
    options: list[str]
    template_id: int

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"BaseMarker(id={self.id}, name={self.name}, description={self.description})"


class CompositeMarkerCreate(BaseModel):
    options: Annotated[dict[str, list[str]], AfterValidator(validators.validate_options)]
    template_id: int

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"CompositeMarker(options={self.options})"


class CompositeMarkerUpdate(BaseModel):
    options: Annotated[Optional[dict[str, list[str]]], AfterValidator(validators.validate_options)]
    template_id: Optional[int]

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"CompositeMarker(options={self.options})"
    

class CompositeMarkerRetrieve(BaseModel):
    id: int
    options: Annotated[dict[str, list[str]], AfterValidator(validators.validate_options)]
    template_id: int

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"CompositeMarker(id={self.id}, options={self.options})"


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

