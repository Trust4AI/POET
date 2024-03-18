from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException

from core.models import models
from core.schemas import schemas
from services import input_service

router = APIRouter()


@router.post("/generate", response_model=List[schemas.Input], tags=["input"])
async def generate_input(n: int = 100):
    result = await input_service.generate_input(n)
    return result


@router.post("/generateWithTemplate", response_model=List[schemas.Input], tags=["input"])
async def generate_with_template(template: Union[List[schemas.TemplateCreateMarker], schemas.TemplateCreateMarker],
                                 n: int = 100, save: bool = False):
    result = await input_service.generate_with_template(template, n, save)
    return result[:n]
