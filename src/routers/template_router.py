from typing import List, Union

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse

from core.models import models
from core.schemas import schemas
from services import template_service

router = APIRouter()


@router.get("", response_model=List[schemas.TemplateRetrieve],
            response_description="Get all templates",
            description="Get all templates",
            summary="Get all templates",
            responses={200: {"description": "List of templates"},
                       500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def get_all_templates():
    try:
        result = await template_service.get_all_templates()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


@router.get(path="/download")
async def download_templates_csv():
    try:
        result = await template_service.download_templates_csv()
        if not result:
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(result, media_type="text/csv", filename=result)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


@router.get("/{template_id}", response_model=schemas.TemplateRetrieve,
            response_description="Get template by id",
            description="Get template by id",
            summary="Get template by id",
            responses={200: {"description": "Template"},
                       404: {"description": "Template not found", "model": schemas.ErrorResponse},
                       500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def get_template_by_id(template_id: int):
    try:

        result = await template_service.get_template_by_id(template_id)

        result = result[0] if result else None

        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        else:
            return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


# @router.post("", response_model=schemas.TemplateRetrieve, status_code=201,
#              response_description="Create a new template",
#              description="Create a new template",
#              summary="Create a new template",
#              responses={201: {"description": "Template created successfully"},
#                         500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def create_template(model: Union[schemas.TemplateCreateMarker, schemas.TemplateBase] = Body(...)):
    try:
        result = await template_service.create_template(model)

        if result:
            if isinstance(result, list):
                return result
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


# @router.put("/{template_id}", response_model=schemas.TemplateRetrieve,
#             response_description="Update template by id",
#             description="Update template by id",
#             summary="Update template by id",
#             responses={200: {"description": "Template updated successfully"},
#                        500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def update_template(template_id: int, model: schemas.TemplateUpdate):
    try:
        if not await template_service.exists(template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await template_service.update_template(template_id, model)

        if result:
            return result[0]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


# @router.delete("/{template_id}", response_model=models.Template,
#                response_description="Delete template by id",
#                description="Delete template by id",
#                summary="Delete template by id",
#                responses={204: {"description": "Template deleted successfully"},
#                           404: {"description": "Template not found", "model": schemas.ErrorResponse},
#                           500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def delete_template(template_id: int):
    try:
        if not await template_service.exists(template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await template_service.delete_template(template_id)

        if result:
            raise HTTPException(status_code=204, detail="Template deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
