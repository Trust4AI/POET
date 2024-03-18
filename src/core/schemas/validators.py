from . import schemas


def validate_options(v):
    if not v:
        raise ValueError("The dictionary must contain at least one key-value pair")
    for key, value in v.items():
        if not value or not all(isinstance(item, str) and item for item in value):
            raise ValueError(f"The list for key {key} must contain at least one non-empty string")
    return v


def validate_type(v):
    if v not in schemas.Type.__members__:
        raise ValueError('Type must be either "bias" or "safety"')
    return v


def validate_expected_result(v):
    if v not in schemas.ExpectedResult.__members__:
        raise ValueError('ExpectedResult must be either "bias" or "safety"')
    return v
