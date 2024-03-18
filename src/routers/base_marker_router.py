from typing import List
from fastapi import APIRouter, HTTPException

from core.models import models
from core.schemas import schemas
from services import base_marker_service, template_service

router = APIRouter()


@router.get("", response_model=List[schemas.BaseMarkerRetrieve], tags=["base_marker"],
            response_description="Get all base markers",
            description="Get all base markers",
            summary="Get all base markers",
            responses={200: {"description": "List of base markers"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def get_all_base_markers():
    try:
        result = await base_marker_service.get_all_base_markers()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
    

@router.get("/template/{template_id}", response_model=list[schemas.BaseMarkerRetrieve], tags=["base_marker"],
            response_description="Get base markers by template id",
            description="Get base markers by template id",
            summary="Get base markers by template id",
            responses={200: {"description": "List of base markers"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
                       404: {"description": "Base markers not found", "model": schemas.ErrorResponse},
                       404: {"description": "Template not found", "model": schemas.ErrorResponse}})
async def get_base_markers_by_template_id(template_id: int):
    try:
        if not await template_service.exists(template_id):
            raise HTTPException(status_code=404, detail="Template not found")
        
        result = await base_marker_service.get_base_markers_by_template_id(template_id)
        if not result:
            raise HTTPException(status_code=404, detail="Base markers not found")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


@router.get("/{base_marker_id}", response_model=schemas.BaseMarkerRetrieve, tags=["base_marker"],
            response_description="Get base marker by id",
            description="Get base marker by id",
            summary="Get base marker by id",
            responses={200: {"description": "Base marker found"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
                       404: {"description": "Base marker not found", "model": schemas.ErrorResponse}})
async def get_base_marker_by_id(base_marker_id: int):
    try:
        result = await base_marker_service.get_base_marker_by_id(base_marker_id)
        if not result:
            raise HTTPException(status_code=404, detail="Base marker not found")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


@router.post("", response_model=schemas.BaseMarkerRetrieve, status_code=201, tags=["base_marker"],
             response_description="Create a new base marker",
             description="Create a new base marker",
             summary="Create a new base marker",
             responses={201: {"description": "Base marker created successfully"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
                        404: {"description": "Template not found", "model": schemas.ErrorResponse}})
async def create_base_marker(model: schemas.BaseMarkerBase):
    try:
        if not await template_service.exists(model.template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await base_marker_service.create_base_marker(model)
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


@router.put("/{base_marker_id}", response_model=models.BaseMarker, tags=["base_marker"],
            response_description="Update a base marker",
            description="Update a base marker",
            summary="Update a base marker",
            responses={200: {"description": "Base marker updated successfully"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
                       404: {"description": "Base marker not found", "model": schemas.ErrorResponse}})
async def update_base_marker(base_marker_id: int, model: schemas.BaseMarkerBase):
    try:
        if not await base_marker_service.exists(base_marker_id):
            raise HTTPException(status_code=404, detail="Base marker not found")

        if model.template_id != None and not await template_service.exists(model.template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await base_marker_service.update_base_marker(base_marker_id, model)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
    

@router.delete("/{base_marker_id}", response_model=models.BaseMarker, tags=["base_marker"],
                response_description="Delete a base marker",
                description="Delete a base marker",
                summary="Delete a base marker",
                responses={204: {"description": "Base marker deleted successfully"}, 500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
                              404: {"description": "Base marker not found", "model": schemas.ErrorResponse}})
async def delete_base_marker(base_marker_id: int):
    try:
        if not await base_marker_service.exists(base_marker_id):
            raise HTTPException(status_code=404, detail="Base marker not found")

        result = await base_marker_service.delete_base_marker(base_marker_id)
        if result:
            raise HTTPException(status_code=204, detail="Base marker deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
    