from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas

from services import template_service


async def get_all_placeholders():
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Placeholder)
            result = await session.exec(query)
            return result.all()
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def get_placeholder_by_id(placeholder_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Placeholder).where(models.Placeholder.id == placeholder_id)
            result = await session.exec(query)
            return result.one()
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def get_placeholders_by_template_id(template_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Placeholder).where(models.Placeholder.template_id == template_id)
            result = await session.exec(query)
            return result.unique().all()
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def create_placeholder(model: schemas.Placeholder):
    base_maker: models.Placeholder = models.Placeholder(
        name=model.name,
        description=model.description,
        options=list(model.values),
        template_id=model.template_id
    )
    try:
        async with AsyncSession(engine_async) as session:
            session.add(base_maker)
            await session.commit()
            await session.refresh(base_maker)
            return base_maker
    except IntegrityError as e:
        raise RuntimeError(f'Integrity Error: {e}')
    except DataError as e:
        raise RuntimeError(f'Data Error: {e}')
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def update_placeholder(placeholder_id: int, model: schemas.PlaceholderUpdate):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Placeholder).where(models.Placeholder.id == placeholder_id)
            result = await session.exec(query)
            placeholder = result.one()
            if model.name:
                placeholder.name = model.name
            if model.description:
                placeholder.description = model.description
            if model.values:
                placeholder.values = model.values

            template = await template_service.get_template_by_id(placeholder.template_id)
            template = template[0]
            for marker in template.placeholders:
                if marker.id == placeholder_id:
                    marker.name = placeholder.name
                    marker.description = placeholder.description
                    marker.values = placeholder.values
                    marker.template_id = None

            templates = await template_service.get_all_templates()
            for t in templates:
                if t.id == template.id:
                    templates.remove(t)
                    break

            for t in templates:
                for tm in t.placeholders:
                    tm.template_id = None
                if t.base == template.base and t.description == template.description and t.expected_result == template.expected_result and _check_same_markers(
                        t.placeholders, template.placeholders):
                    raise Exception("Template with the same base, description, "
                                    "expected result and markers already exists")

            await session.commit()
            await session.refresh(placeholder)
            return placeholder
    except IntegrityError as e:
        raise RuntimeError(f'Integrity Error: {e}')
    except DataError as e:
        raise RuntimeError(f'Data Error: {e}')
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def delete_placeholder(placeholder_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Placeholder).where(models.Placeholder.id == placeholder_id)
            result = await session.exec(query)
            placeholder = result.one()
            await session.delete(placeholder)
            await session.commit()
            return placeholder
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        RuntimeError(e)


async def exists(placeholder_id: int):
    placeholder = await get_placeholder_by_id(placeholder_id)
    return True if placeholder else False


async def check_template_markers_exists(model: [schemas.PlaceholderBase], template_id: int):
    try:
        markers = await get_placeholders_by_template_id(template_id)
        markers = [schemas.PlaceholderBase(name=marker.name, description=marker.description, options=marker.values)
                   for marker in markers]
        if model == markers:
            return True
        return False

    except Exception as e:
        RuntimeError(e)


def _check_same_markers(markers1: [schemas.Placeholder], markers2: [schemas.Placeholder]):
    if len(markers1) != len(markers2):
        return False
    trues = []
    for marker1 in markers1:
        for marker2 in markers2:
            if marker1.name == marker2.name and marker1.description == marker2.description and set(
                    marker1.values) == set(marker2.values):
                trues.append(True)
    return len(trues) == len(markers1)
