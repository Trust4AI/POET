import uuid
from typing import Union
import pandas as pd
from fastapi import HTTPException

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError, NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas
from services import placeholder_service


async def get_all_templates():
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template, models.Placeholder).join(models.Placeholder, isouter=True)
            result = await session.exec(query)
            return await _transform_results_to_template_retrieve(result.unique().all())
    except IntegrityError as e:
        raise RuntimeError(f'Integrity Error: {e}')
    except DataError as e:
        raise RuntimeError(f'Data Error: {e}')
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def get_template_by_id(template_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template, models.Placeholder).join(models.Placeholder, isouter=True).where(
                models.Template.id == template_id)
            result = await session.exec(query)
            return await _transform_results_to_template_retrieve(result.all())

    except NoResultFound:
        return None
    except Exception as e:
        RuntimeError(e)


async def create_template(model: Union[schemas.TemplateCreateMarker, schemas.TemplateBase]):
    if 'markers' not in model.dict() or not model.placeholders:
        return await create_template_without_markers(model)
    else:
        return await create_template_with_markers(model)


async def create_template_without_markers(model: schemas.TemplateBase):
    template: models.Template = models.Template(
        base=model.base,
        description=model.description,
        expected_result=model.expected_result if hasattr(model, 'expected_result') else "positive"
    )
    try:
        async with AsyncSession(engine_async) as session:
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template
    except Exception as e:
        RuntimeError(e)


async def create_template_with_markers(model: schemas.TemplateCreateMarker):
    try:
        template_base: schemas.TemplateBase = schemas.TemplateBase(
            base=model.base,
            description=model.description,
            expected_result=model.expected_result
        )
        exists_template = await _check_template_base_exists(template_base)
        if exists_template:
            exists_markers = []
            for et in exists_template:
                exists_marker = await placeholder_service.check_template_markers_exists(model.placeholders, et.id)
                exists_markers.append(exists_marker)
            if exists_markers and True in exists_markers:
                index_true = exists_markers.index(True)
                return await get_template_by_id(exists_template[index_true].id)
        template = await create_template(template_base)
        template_retrieve: schemas.TemplateRetrieve = schemas.TemplateRetrieve(
            id=template.id,
            base=template.base,
            description=template.description,
            expected_result=template.expected_result,
            markers=[]
        )

        for marker in model.placeholders:
            marker: schemas.Placeholder = schemas.Placeholder(
                name=marker.name,
                description=marker.description,
                options=marker.values,
                template_id=template_retrieve.id
            )
            placeholder = await placeholder_service.create_placeholder(marker)
            placeholder: schemas.PlaceholderRetrieve = schemas.PlaceholderRetrieve(
                id=placeholder.id,
                name=placeholder.name,
                description=placeholder.description,
                options=placeholder.values,
                template_id=placeholder.template_id
            )
            template_retrieve.placeholders.append(placeholder)

        return template_retrieve
    except Exception as e:
        RuntimeError(e)


async def update_template(template_id: int, model: schemas.TemplateUpdate):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template).where(models.Template.id == template_id)
            result = await session.exec(query)
            template = result.one()
            if model.base:
                template.base = model.base
            if model.description:
                template.description = model.description
            if model.expected_result:
                template.expected_result = model.expected_result
            await session.commit()
            await session.refresh(template)
            return await get_template_by_id(template_id)
    except Exception as e:
        RuntimeError(e)


async def delete_template(template_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            template = await session.get(models.Template, template_id)
            await session.delete(template)
            await session.commit()
            return template
    except Exception as e:
        RuntimeError(e)


async def exists(template_id: int):
    template = await get_template_by_id(template_id)
    template = template[0] if template else None
    return True if template else False


async def _transform_results_to_template_retrieve(result):
    templates_dict = {}

    if not result:
        return []
    for template, placeholder in result:

        if template.id not in templates_dict:
            templates_dict[template.id] = schemas.TemplateRetrieve(
                id=template.id,
                base=template.base,
                description=template.description,
                expected_result=template.expected_result,
                placeholders=[]
            )

        if placeholder:
            placeholder_retrieve = schemas.PlaceholderRetrieve(
                id=placeholder.id,
                name=placeholder.name,
                description=placeholder.description,
                values=placeholder.values,
                template_id=placeholder.template_id
            )

            if placeholder_retrieve not in templates_dict[template.id].placeholders:
                templates_dict[template.id].placeholders.append(placeholder_retrieve)

    return list(templates_dict.values())


async def _check_template_base_exists(model: schemas.TemplateBase):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template).where(func.trim(models.Template.base) == model.base.strip())
            result = await session.exec(query)
            return result.all()
    except NoResultFound:
        return None
    except Exception as e:
        RuntimeError(e)


async def download_templates_csv():
    try:
        templates = await get_all_templates()  # Asumiendo que esta función devuelve una lista de objetos Template
        if not templates:
            raise HTTPException(status_code=404, detail="No templates found")

        # Crear un DataFrame de Pandas a partir de los datos
        csv_data = pd.DataFrame([template.dict() for template in templates])

        # Generar un nombre de archivo único para evitar conflictos de concurrencia
        file_name = f'./src/downloads/template-{uuid.uuid4()}.csv'
        csv_data.to_csv(file_name, index=False)

        return file_name
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
