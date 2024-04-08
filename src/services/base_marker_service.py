from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas

from services import template_service


async def get_all_base_markers():
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.BaseMarker)
            result = await session.exec(query)
            return result.all()
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def get_base_marker_by_id(base_marker_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.BaseMarker).where(models.BaseMarker.id == base_marker_id)
            result = await session.exec(query)
            return result.one()
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def get_base_markers_by_template_id(template_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.BaseMarker).where(models.BaseMarker.template_id == template_id)
            result = await session.exec(query)
            return result.unique().all()
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def create_base_marker(model: schemas.BaseMarker):
    base_maker: models.BaseMarker = models.BaseMarker(
        name=model.name,
        description=model.description,
        options=list(model.options),
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


async def update_base_marker(base_marker_id: int, model: schemas.BaseMarkerUpdate):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.BaseMarker).where(models.BaseMarker.id == base_marker_id)
            result = await session.exec(query)
            base_marker = result.one()
            if model.name:
                base_marker.name = model.name
            if model.description:
                base_marker.description = model.description
            if model.options:
                base_marker.options = model.options

            template = await template_service.get_template_by_id(base_marker.template_id)
            template = template[0]
            for marker in template.markers:
                if marker.id == base_marker_id:
                    marker.name = base_marker.name
                    marker.description = base_marker.description
                    marker.options = base_marker.options
                    marker.template_id = None

            templates = await template_service.get_all_templates()
            for t in templates:
                if t.id == template.id:
                    templates.remove(t)
                    break

            for t in templates:
                for tm in t.markers:
                    tm.template_id = None
                if t.base == template.base and t.description == template.description and t.expected_result == template.expected_result and _check_same_markers(
                        t.markers, template.markers):
                    raise Exception("Template with the same base, description, "
                                    "expected result and markers already exists")

            await session.commit()
            await session.refresh(base_marker)
            return base_marker
    except IntegrityError as e:
        raise RuntimeError(f'Integrity Error: {e}')
    except DataError as e:
        raise RuntimeError(f'Data Error: {e}')
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        raise RuntimeError(e)


async def delete_base_marker(base_marker_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.BaseMarker).where(models.BaseMarker.id == base_marker_id)
            result = await session.exec(query)
            base_marker = result.one()
            await session.delete(base_marker)
            await session.commit()
            return base_marker
    except SQLAlchemyError as e:
        raise RuntimeError(f'Unknown error of SQLAlchemy: {e}')
    except Exception as e:
        RuntimeError(e)


async def exists(base_marker_id: int):
    base_marker = await get_base_marker_by_id(base_marker_id)
    return True if base_marker else False


async def check_template_markers_exists(model: [schemas.BaseMarkerBase], template_id: int):
    try:
        markers = await get_base_markers_by_template_id(template_id)
        markers = [schemas.BaseMarkerBase(name=marker.name, description=marker.description, options=marker.options)
                   for marker in markers]
        if model == markers:
            return True
        return False

    except Exception as e:
        RuntimeError(e)


def _check_same_markers(markers1: [schemas.BaseMarker], markers2: [schemas.BaseMarker]):
    if len(markers1) != len(markers2):
        return False
    trues = []
    for marker1 in markers1:
        for marker2 in markers2:
            if marker1.name == marker2.name and marker1.description == marker2.description and set(
                    marker1.options) == set(marker2.options):
                trues.append(True)
    return len(trues) == len(markers1)
