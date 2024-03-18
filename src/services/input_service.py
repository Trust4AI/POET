from typing import Union, List

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas
from services import template_service

from itertools import chain


async def generate_input(n):
    try:
        async with AsyncSession(engine_async) as session:
            templates = cast_templates(await template_service.get_all_templates())
            result = [template.build(n) for template in templates]
            result = list(chain.from_iterable(result))
            print(result)
            return cast_input(result)
    except Exception as e:
        RuntimeError(e)


async def generate_with_template(template: Union[List[schemas.TemplateCreateMarker], schemas.TemplateCreateMarker],
                                 n: int, save):
    if save and isinstance(template, List):
        return await _generate_with_templates(template, n)
    elif save and not isinstance(template, List):
        return await _generate_with_template(template, n)
    elif not save and isinstance(template, List):
        return await _generate_with_templates_whithout_save(template, n)
    elif not save and not isinstance(template, List):
        print("1", template, n)
        return await _generate_with_template_whithout_save(template, n)


async def _generate_with_template(template: schemas.TemplateCreateMarker, n):
    template = await template_service.create_template(template)
    template = schemas.Template(**template.__dict__)
    result = template.build(n)
    return cast_input(result)


async def _generate_with_templates(templates: List[schemas.TemplateCreateMarker], n):
    result = []
    print(templates)
    for template in templates:
        result.extend(await _generate_with_template(template, n))
    return result


async def _generate_with_template_whithout_save(template: schemas.TemplateCreateMarker, n):
    template = schemas.Template(**template.__dict__)
    return cast_input(template.build(n))


async def _generate_with_templates_whithout_save(templates: List[schemas.TemplateCreateMarker], n):
    result = []
    for template in templates:
        result.extend(await _generate_with_template_whithout_save(template, n))
    return result


def cast_templates(templates):
    return [schemas.Template(**template.__dict__) for template in templates]


def cast_input(inputs):
    return [schemas.Input(query=input, type="bias", expected_result=inputs[1]) for input in inputs[0]]
