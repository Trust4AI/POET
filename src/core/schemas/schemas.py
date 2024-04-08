from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, constr, Field
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator

from . import validators


class TemplateBase(BaseModel):
    base: constr(min_length=1, max_length=255) = Field(..., description="Base string", example="Hello, {name}!")
    description: constr(min_length=1, max_length=255) = Field(..., description="Description of the template",
                                                              example="A simple greeting")
    expected_result: constr(min_length=1, max_length=255) = Field(..., description="Expected result",
                                                                  example="Hello, John!")

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"Template(base={self.base}, description={self.description})"


class Template(TemplateBase):
    markers: list['BaseMarker']

    def build(self, n: int):
        total_combinations = self.total_unique_combinations()
        result = []

        built_string = self.base

        if total_combinations < n:

            if len(self.markers) == 1:
                result.extend(self.markers[0].replace(self.base))
                return result, self.expected_result
            dict_markers = [{f"{marker.name}": o} for marker in self.markers for o in marker.options]

            dm = []

            for d in dict_markers:
                dmd = []
                k1 = list(d.keys())[0]
                v1 = list(d.values())[0]
                dmd.append({k1: v1})
                for d2 in dict_markers:
                    k2 = list(d2.keys())[0]
                    v2 = list(d2.values())[0]

                    if k1 != k2 and v1 != v2:
                        dmd.append({k2: v2})
                dm.append(dmd)

            for d in dm:
                _k = list(d[0].keys())[0]
                _v = list(d[0].values())[0]
                _built_string = built_string.replace(_k, _v)
                for d_ in d[1:]:
                    k = list(d_.keys())[0]
                    v = list(d_.values())[0]
                    __built_string = _built_string.replace(k, v)
                    result.append(__built_string)

        else:
            while len(result) < total_combinations and len(result) < n:
                if len(self.markers) == 1:
                    result.extend(self.markers[0].replace(self.base))
                    return result, self.expected_result
                dict_markers = [{f"{marker.name}": o} for marker in self.markers for o in marker.options]

                dm = []

                for d in dict_markers:
                    dmd = []
                    k1 = list(d.keys())[0]
                    v1 = list(d.values())[0]
                    dmd.append({k1: v1})
                    for d2 in dict_markers:
                        k2 = list(d2.keys())[0]
                        v2 = list(d2.values())[0]

                        if k1 != k2 and v1 != v2:
                            dmd.append({k2: v2})
                    dm.append(dmd)

                for d in dm:
                    _k = list(d[0].keys())[0]
                    _v = list(d[0].values())[0]
                    _built_string = built_string.replace(_k, _v)
                    for d_ in d[1:]:
                        k = list(d_.keys())[0]
                        v = list(d_.values())[0]
                        __built_string = _built_string.replace(k, v)
                        result.append(__built_string)

                if len(result) > n:
                    result = result[:n]
        return result, self.expected_result, self.description

    def total_unique_combinations(self):
        total_combinations = 1
        for marker in self.markers:
            total_combinations *= len(marker.options)
        return total_combinations


class TemplateCreateMarker(TemplateBase):
    markers: list['BaseMarkerBase']

    def __repr__(self):
        return f"Template(base={self.base}, description={self.description}, markers={self.markers})"


class TemplateUpdate(BaseModel):
    base: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Base string",
                                                                 example="Hello, {name}!")
    description: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Description of the template",
                                                                        example="A simple greeting")
    expected_result: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Expected result",
                                                                            example="Hello, John!")

    class Config:
        from_attributes = True

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
    options: List[str] = Field(..., description="List of options", example=["John", "Jane"])

    class Config:
        from_attributes = True

    def __repr__(self):
        return (f"BaseMarker(name={self.name}, description={self.description}, options={self.options}, "
                f"template_id={self.template_id if 'template_id' in self.__dict__ else None})")


class BaseMarker(BaseMarkerBase):
    template_id: Optional[int] = Field(None, description="Template id")

    def replace(self, base: str) -> list[str]:
        return [base.replace(self.name, option) for option in self.options]


class BaseMarkerRetrieve(BaseMarkerBase):
    id: int
    template_id: int = Field(None, description="Template id")


class BaseMarkerUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Name of the marker",
                                                                 example="{name}")
    description: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Description of the marker",
                                                                        example="Name of the person")
    options: Optional[List[str]] = Field(None, description="List of options", example=["John", "Jane"])

    template_id: Optional[int] = Field(None, description="Template id")

    class Config:
        from_attributes = True

    def __repr__(self):
        return (f"BaseMarker(name={self.name}, description={self.description}, options={self.options}, "
                f"template_id={self.template_id if 'template_id' in self.__dict__ else None})")


class Type(str, Enum):
    bias = "bias"
    safety = "safety"


class Input(BaseModel):
    query: constr(min_length=1, max_length=255)
    type: constr(min_length=1, max_length=255) = Field(None, description="Type of the input", example="bias")
    expected_result: constr(min_length=1, max_length=255) = Field(None, description="Expected result",
                                                                  example="Hello, John!")

    class Config:
        from_attributes = True


class TestResult(BaseModel):
    input: str
    output: str
    evaluation_result: str
    evaluation_type: str


class ErrorResponse(BaseModel):
    detail: str
