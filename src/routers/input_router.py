from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException

from core.models import models
from core.schemas import schemas
from services import input_service

router = APIRouter()


@router.get("/generate", response_model=List[schemas.Input],
             response_description="Generate inputs",
             description="Generate inputs",
             summary="Generate inputs",
             responses={200: {"description": "List of inputs"},
                        500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def generate_input(n: int = 100):
    result = await input_service.generate_input(n)
    if result is None:
        return []
    return result


@router.post("/generateWithTemplate", response_model=List[schemas.Input],
             response_description="Generate inputs with a template",
             description="Generate inputs with a template",
             summary="Generate inputs with a template",
             responses={200: {"description": "List of inputs"},
                        500: {"description": "Internal Server Error", "model": schemas.ErrorResponse}})
async def generate_with_template(template: schemas.TemplateCreateMarker, n: int = 100,
                                 mode: str = Union["random", "exhaustive"]):
    result = await input_service.generate_with_template(template, n, mode)
    return result[:n]


@router.get("/generateWithTemplateId", response_model=List[schemas.Input],
            response_description="Generate inputs with a template",
            description="Generate inputs with a template",
            summary="Generate inputs with a template",
            responses={200: {"description": "List of inputs"},
                       500: {"description": "Internal Server Error"}})
async def generate_with_template_id(template_id: int, n: int = 100,
                                    mode: str = Union["random", "sequential"]):
    result = await input_service.generate_with_template_id(template_id, n, mode)
    return result[:n]
