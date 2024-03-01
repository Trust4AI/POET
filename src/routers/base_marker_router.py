from fastapi import APIRouter, HTTPException

from core.models import models
from core.schemas import schemas
from services import base_marker_service, template_service

router = APIRouter()


@router.get("", response_model=models.BaseMarker, tags=["base_marker"],
            response_description="Get all base markers",
            description="Get all base markers",
            summary="Get all base markers",
            responses={200: {"description": "List of base markers"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def get_base_markers():
    try:
        result = await base_marker_service.get_all_base_markers()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
    

@router.get("/template/{template_id}", response_model=models.BaseMarker, tags=["base_marker"],
            response_description="Get base markers by template id",
            description="Get base markers by template id",
            summary="Get base markers by template id",
            responses={200: {"description": "List of base markers"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def get_base_markers_by_template_id(template_id: int):
    try:
        result = await base_marker_service.get_base_markers_by_template_id(template_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))



@router.post("", response_model=models.BaseMarker, status_code=201, tags=["base_marker"],
             response_description="Create a new base marker",
             description="Create a new base marker",
             summary="Create a new base marker",
             responses={201: {"description": "Base marker created successfully"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
                        404: {"description": "Template not found", "model": schemas.ErrorResponse}})
async def create_base_marker(model: schemas.BaseMarkerCreate):
    try:
        template = await template_service.get_template_by_id(model.template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        result = await base_marker_service.create_base_marker(model)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
