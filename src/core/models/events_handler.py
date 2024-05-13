from sqlalchemy import event

from core.models.models import Placeholder
from services import placeholder_service


@event.listens_for(Placeholder, "before_insert")
async def validate_options_before_insert(mapper, connection, target):
    template_markers = await placeholder_service.get_placeholders_by_template_id(target.template_id)
    existing_options = set()
    for marker in template_markers:
        existing_options.update(marker.values)
    if any(option in existing_options for option in target.values):
        raise ValueError("Options must be unique within a template")
