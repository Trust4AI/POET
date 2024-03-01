from fastapi import APIRouter, Depends, HTTPException

from core.models import models
from core.schemas import schemas
from services import input_service

router = APIRouter()


@router.post("/generate", response_model=schemas.Input, tags=["input"])
async def generate_input():
    return await input_service.generate_input()


@router.post("/generateWithTemplate", response_model=schemas.Input, tags=["input"])
async def generate_with_template(template: schemas.TemplateCreate):
    return await input_service.generate_with_template(template)
