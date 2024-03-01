from . import schemas

def validate_options(self, v):
    if not v:
        raise ValueError('Options cannot be empty')
    return v

def validate_type(self, v):
    if v not in schemas.Type.__members__:
        raise ValueError('Type must be either "bias" or "safety"')
    return v