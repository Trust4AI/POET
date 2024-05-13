from typing import List
from fastapi import APIRouter, HTTPException

from core.schemas import schemas
from services import placeholder_service, template_service

router = APIRouter()


@router.get("", response_model=List[schemas.PlaceholderRetrieve],
            response_description="Get all placeholders",
            description="Get all placeholders",
            summary="Get all placeholders",
            responses={200: {"description": "List of placeholders"},
                       500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def get_all_placeholders():
    try:
        result = await placeholder_service.get_all_placeholders()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


@router.get("/template/{template_id}", response_model=list[schemas.PlaceholderRetrieve],
            response_description="Get placeholders by template id",
            description="Get placeholders by template id",
            summary="Get placeholders by template id",
            responses={200: {"description": "List of placeholders"},
                       500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
                       404: {"description": "placeholders not found", "model": schemas.ErrorResponse},
                       404: {"description": "Template not found", "model": schemas.ErrorResponse}})
async def get_placeholders_by_template_id(template_id: int):
    try:
        if not await template_service.exists(template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await placeholder_service.get_placeholders_by_template_id(template_id)
        if not result:
            raise HTTPException(status_code=404, detail="placeholders not found")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


@router.get("/{placeholder_id}", response_model=schemas.PlaceholderRetrieve,
            response_description="Get placeholder by id",
            description="Get placeholder by id",
            summary="Get placeholder by id",
            responses={200: {"description": "placeholder found"},
                       500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
                       404: {"description": "placeholder not found", "model": schemas.ErrorResponse}})
async def get_placeholder_by_id(placeholder_id: int):
    try:
        result = await placeholder_service.get_placeholder_by_id(placeholder_id)
        if not result:
            raise HTTPException(status_code=404, detail="placeholder not found")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


# @router.post("", response_model=schemas.PlaceholderRetrieve, status_code=201,
#              response_description="Create a new placeholder",
#              description="Create a new placeholder",
#              summary="Create a new placeholder",
#              responses={201: {"description": "placeholder created successfully"},
#                         500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
#                         404: {"description": "Template not found", "model": schemas.ErrorResponse}})
async def create_placeholder(model: schemas.Placeholder):
    try:
        if not await template_service.exists(model.template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await placeholder_service.create_placeholder(model)
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


# @router.put("/{placeholder_id}", response_model=models.Placeholder,
#             response_description="Update a placeholder",
#             description="Update a placeholder",
#             summary="Update a placeholder",
#             responses={200: {"description": "placeholder updated successfully"},
#                        500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
#                        404: {"description": "placeholder not found", "model": schemas.ErrorResponse}})
async def update_placeholder(placeholder_id: int, model: schemas.PlaceholderUpdate):
    try:
        if not await placeholder_service.exists(placeholder_id):
            raise HTTPException(status_code=404, detail="placeholder not found")

        if model.template_id != None and not await template_service.exists(model.template_id):
            raise HTTPException(status_code=404, detail="Template not found")

        result = await placeholder_service.update_placeholder(placeholder_id, model)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


# @router.delete("/{placeholder_id}", response_model=models.Placeholder,
#                response_description="Delete a placeholder",
#                description="Delete a placeholder",
#                summary="Delete a placeholder",
#                responses={204: {"description": "placeholder deleted successfully"},
#                           500: {"description": "Internal Server Error", "model": schemas.ErrorResponse},
#                           404: {"description": "placeholder not found", "model": schemas.ErrorResponse}})
async def delete_placeholder(placeholder_id: int):
    try:
        if not await placeholder_service.exists(placeholder_id):
            raise HTTPException(status_code=404, detail="placeholder not found")

        result = await placeholder_service.delete_placeholder(placeholder_id)
        if result:
            raise HTTPException(status_code=204, detail="placeholder deleted successfully")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
