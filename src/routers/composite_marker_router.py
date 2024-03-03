from fastapi import APIRouter, HTTPException

from core.models import models
from core.schemas import schemas
from services import composite_marker_service, template_service

router = APIRouter()

@router.get("", response_model=list[schemas.CompositeMarkerRetrieve], status_code=200, tags=["composite_marker"],
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
    
@router.get("/template/{template_id}", response_model=list[schemas.CompositeMarkerRetrieve], status_code=200, tags=["composite_marker"],
            description="Get all composite markers by template id",
            summary="Get all composite markers by template id",
            response_description="List of composite markers",
            responses={200: {"description": "List of composite markers"}, 404: {"description": "Template not found", "model": schemas.ErrorResponse},
                       500: {"description": "Internal Server Error"}})
async def get_all_composite_markers_by_template_id(template_id: int):
    try:
        if not await template_service.exists(template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await composite_marker_service.get_all_composite_markers_by_template_id(template_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{composite_marker_id}", response_model=schemas.CompositeMarkerRetrieve, status_code=200, tags=["composite_marker"],
            description="Get composite marker by id",
            summary="Get composite marker by id",
            response_description="Composite marker found",
            responses={200: {"description": "Composite marker found"}, 404: {"description": "Composite marker not found", "model": schemas.ErrorResponse},
                       500: {"description": "Internal Server Error"}})
async def get_composite_marker_by_id(composite_marker_id: int):
    try:
        result = await composite_marker_service.get_composite_marker_by_id(composite_marker_id)
        if not result:
            raise HTTPException(status_code=404, detail="Composite marker not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=schemas.CompositeMarkerRetrieve, status_code=201, tags=["composite_marker"])
async def create_composite_marker(model: schemas.CompositeMarkerCreate):
    try: 
        if not await template_service.exists(model.template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await composite_marker_service.create_composite_marker(model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/{composite_marker_id}", response_model=schemas.CompositeMarkerRetrieve, status_code=200, tags=["composite_marker"],
            description="Update composite marker by id",
            summary="Update composite marker by id",
            response_description="Composite marker updated",
            responses={200: {"description": "Composite marker updated"}, 404: {"description": "Composite marker not found", "model": schemas.ErrorResponse},
                       404: {"description": "Template not found"} ,500: {"description": "Internal Server Error"}})
async def update_composite_marker(composite_marker_id: int, model: schemas.CompositeMarkerUpdate):
    try:

        if not await composite_marker_service.exists(composite_marker_id):
            raise HTTPException(status_code=404, detail="Composite marker not found")

        if model.template_id != None and not await template_service.exists(model.template_id):
            raise HTTPException(status_code=404, detail="Template not found")
        
        result = await composite_marker_service.update_composite_marker(composite_marker_id, model)
        print('result2', result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@router.delete("/{composite_marker_id}", response_model=schemas.CompositeMarkerRetrieve, status_code=200, tags=["composite_marker"],
               description="Delete composite marker by id",
                summary="Delete composite marker by id",
                response_description="Composite marker deleted",
                responses={200: {"description": "Composite marker deleted"}, 404: {"description": "Composite marker not found", "model": schemas.ErrorResponse},
                        204:{"description": "Template deleted succesfully"} ,500: {"description": "Internal Server Error"}})
async def delete_composite_marker(composite_marker_id: int):
    try:
        if not await composite_marker_service.exists(composite_marker_id):
            raise HTTPException(status_code=404, detail="Composite marker not found")
        
        result = await composite_marker_service.delete_composite_marker(composite_marker_id)
        
        if result:
            raise HTTPException(status_code=204, detail="Template deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
