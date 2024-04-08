from sqlalchemy import event
from sqlmodel import Session, select

from core.models.models import BaseMarker
from services import base_marker_service


@event.listens_for(BaseMarker, "before_insert")
async def validate_options_before_insert(mapper, connection, target):
    template_markers = await base_marker_service.get_base_markers_by_template_id(target.template_id)
    existing_options = set()
    for marker in template_markers:
        existing_options.update(marker.options)
    if any(option in existing_options for option in target.options):
        raise ValueError("Options must be unique within a template")
