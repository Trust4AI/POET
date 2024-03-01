from fastapi import APIRouter, HTTPException

from core.models import models
from core.schemas import schemas
from services import composite_marker_service, template_service

router = APIRouter()

@router.get("", response_model=list[models.CompositeMarker], status_code=200, tags=["composite_marker"],
            description="Get all composite markers",
            summary="Get all composite markers",
            response_description="List of composite markers",
            responses={200: {"description": "List of composite markers"}, 500: {"description": "Internal Server Error"}})
async def get_all_composite_markers():
    try: 
        result = await composite_marker_service.get_all_composite_markers()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/template/{template_id}", response_model=models.CompositeMarker, status_code=200, tags=["composite_marker"],
            description="Get all composite markers by template id",
            summary="Get all composite markers by template id",
            response_description="List of composite markers",
            responses={200: {"description": "List of composite markers"}, 404: {"description": "Template not found", "model": schemas.ErrorResponse},
                       500: {"description": "Internal Server Error"}})
async def get_all_composite_markers_by_template_id(template_id: int):
    try:
        template = await template_service.get_template_by_id(template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        result = await composite_marker_service.get_all_composite_markers_by_template_id(template_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=models.CompositeMarker, status_code=201, tags=["composite_marker"])
async def create_composite_marker(model: schemas.CompositeMarkerCreate):
    try: 
        template = await template_service.get_template_by_id(model.template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        result = await composite_marker_service.create_composite_marker(model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{id}", response_model=models.CompositeMarker, status_code=200, tags=["composite_marker"])
async def delete_composite_marker(id: int):
    try:
        result = await composite_marker_service.delete_composite_marker(id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
