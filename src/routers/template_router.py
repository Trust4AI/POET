from typing import List, Union, Literal

from fastapi import APIRouter, HTTPException, Body, Query
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

@router.get(
    path="/download",
    summary="Download Templates CSV",
    description=(
        "This endpoint generates and downloads a CSV file containing template data. "
        "The `mode` parameter determines the generation strategy:\n\n"
        "- `random`: Generates a random subset of templates.\n"
        "- `exhaustive`: Generates all possible combinations of templates.\n\n"
        "The CSV includes the following columns:\n\n"
        "- `template_id`: Identifier of the template.\n"
        "- `number_placeholders`: Number of placeholders in the template.\n"
        "- `group_1`, `group_2`, ..., `group_n`: Values for dynamic groups in the template.\n"
        "- `biased_statement`: The biased statement for the template.\n"
        "- `prompt`: The generated prompt.\n"
        "- `oracle_type`: Type of oracle used (e.g., yes/no, three reasons).\n"
        "- `expected_result`: The expected result for the template."
    ),
    response_description="A CSV file with template data.",
    responses={
        200: {
            "description": "The CSV file was generated successfully.",
            "content": {
                "text/csv": {
                    "example": (
                        "template_id,number_placeholders,group_1,group_2,biased_statement,prompt,oracle_type,expected_result\n"
                        "temp1,3,val1,val2,Bias1,Prompt1,yes_no,Expected1\n"
                        "temp2,2,val3,,Bias2,Prompt2,mc,Expected2\n"
                    )
                }
            },
        },
        500: {"description": "Internal Server Error."},
    },
)
async def download_templates_csv(
    n: int = Query(default=None, description="Number of templates to include in the CSV. Optional."),
    mode: Literal["random", "exhaustive"] = Query(
        default="random", description="Mode of template generation. Must be 'random' or 'exhaustive'."
    ),
):
    """
    Endpoint to download templates as a CSV file.
    """
    try:
        result = await template_service.download_templates_csv(n, mode)
        if not result:
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(result, media_type="text/csv", filename=result)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))



@router.get(
    path="/download_by_template_id",
    summary="Download Templates CSV by Template ID",
    description=(
        "This endpoint generates and downloads a CSV file containing template data for a specific template ID. "
        "The `template_id` parameter is used to filter the templates to be included in the CSV.\n\n"
        "The CSV includes the following columns:\n\n"
        "- `template_id`: Identifier of the template.\n"
        "- `number_placeholders`: Number of placeholders in the template.\n"
        "- `group_1`, `group_2`, ..., `group_n`: Values for dynamic groups in the template.\n"
        "- `biased_statement`: The biased statement for the template.\n"
        "- `prompt`: The generated prompt.\n"
        "- `oracle_type`: Type of oracle used (e.g., yes/no, three reasons).\n"
        "- `expected_result`: The expected result for the template."
    ),
    response_description="A CSV file with template data for the specified template ID.",
    responses={
        200: {
            "description": "The CSV file was generated successfully.",
            "content": {
                "text/csv": {
                    "example": (
                        "template_id,number_placeholders,group_1,group_2,biased_statement,prompt,oracle_type,expected_result\n"
                        "temp1,3,val1,val2,Bias1,Prompt1,yes_no,Expected1\n"
                    )
                }
            },
        },
        422: {"description": "Invalid template ID provided."},
        500: {"description": "Internal Server Error."},
    },
)
async def download_templates_csv_by_id(
    template_id: str = Query(..., description="The ID of the template to include in the CSV."),
    n: int = Query(default=None, description="Number of templates to include in the CSV. Optional."),
    mode: Literal["random", "exhaustive"] = Query(
        default="random", description="Mode of template generation. Must be 'random' or 'exhaustive'."
    ),
):
    """
    Endpoint to download templates as a CSV file filtered by template ID.
    """
    try:
        # Call the service function, passing the template_id to filter.
        result = await template_service.download_templates_csv(template_id=template_id, n=n, mode=mode)
        if not result:
            raise HTTPException(status_code=404, detail="File not found for the specified template ID")
        return FileResponse(result, media_type="text/csv", filename=f"{template_id}_templates.csv")
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
async def get_template_by_id(template_id: str):
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
