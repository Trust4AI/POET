from enum import Enum
from typing import Optional

from pydantic import BaseModel, constr, Field
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator

from . import validators


class ExpectedResult(str, Enum):
    positive = "positive"
    negative = "negative"


class TemplateBase(BaseModel):
    base: constr(min_length=1, max_length=255) = Field(..., description="Base string", example="Hello, {name}!")
    description: constr(min_length=1, max_length=255) = Field(..., description="Description of the template",
                                                              example="A simple greeting")
    expected_result: Annotated[ExpectedResult, AfterValidator(validators.validate_expected_result)] = Field(
        "positive", description="Expected result")

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"Template(base={self.base}, description={self.description})"


class Template(TemplateBase):
    markers: list['BaseMarker']

    def build(self, n: int):
        total_combinations = self.total_unique_combinations()
        result = []

        if total_combinations < n:
            built_string = self.base
            for marker in self.markers:
                built_string = marker.replace(built_string)
            result.extend(built_string)
        else:
            while len(result) < total_combinations and len(result) < n:
                for marker in self.markers:
                    result.extend(marker.replace(self.base))
                if len(result) > n:
                    result = result[:n]
        return result

    def total_unique_combinations(self):
        total_combinations = 1
        for marker in self.markers:
            total_combinations *= len(marker.options)
        return total_combinations


class TemplateCreateMarker(TemplateBase):
    markers: list['BaseMarkerBase']

    def __repr__(self):
        return f"Template(base={self.base}, description={self.description}, markers={self.markers})"


class TemplateRetrieve(TemplateBase):
    id: int
    markers: list['BaseMarkerRetrieve']

    def __repr__(self):
        return f"Template(id={self.id}, base={self.base}, description={self.description}, markers={self.markers})"


class BaseMarkerBase(BaseModel):
    name: constr(min_length=1, max_length=255) = Field(..., description="Name of the marker", example="{name}")
    description: constr(min_length=1, max_length=255) = Field(..., description="Description of the marker",
                                                              example="Name of the person")
    options: list[str] = Field(..., description="List of options", example=["John", "Jane"])
    template_id: Optional[int] = Field(None, description="Template id")

    class Config:
        from_attributes = True

    def __repr__(self):
        return (f"BaseMarker(name={self.name}, description={self.description}, options={self.options}, "
                f"template_id={self.template_id})")


class BaseMarker(BaseMarkerBase):
    def replace(self, base: str) -> list[str]:
        return [base.replace(self.name, option) for option in self.options]


class BaseMarkerRetrieve(BaseMarkerBase):
    id: int


class Type(str, Enum):
    bias = "bias"
    safety = "safety"


class Input(BaseModel):
    query: constr(min_length=1, max_length=255)
    type: Annotated[Type, AfterValidator(validators.validate_type)]

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str
