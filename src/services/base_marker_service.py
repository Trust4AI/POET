from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas


async def get_all_base_markers():
    try:
        async with AsyncSession(engine_async) as session:
            quety = select(models.BaseMarker)
            result = await session.exec(quety)
            return result.all()
    except Exception as e:
        RuntimeError(e)

async def get_base_marker_by_id(base_marker_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.BaseMarker).where(models.BaseMarker.id == base_marker_id)
            result = await session.exec(query)
            return result.one()

    except Exception as e:
        RuntimeError(e)


async def get_base_markers_by_template_id(template_id: int):
    try:
       async with AsyncSession(engine_async) as session:
            qeury = select(models.BaseMarker).where(models.BaseMarker.template_id == template_id)
            result = await session.exec(qeury)
            return result.unique()

    except Exception as e:
        RuntimeError(e)


async def create_base_marker(model: schemas.BaseMarkerBase):
    base_maker: models.BaseMarker = models.BaseMarker(
        name=model.name,
        description=model.description,
        options=model.options,
        template_id=model.template_id
    )
    try:
        async with AsyncSession(engine_async) as session:
            session.add(base_maker)
            await session.commit()
            await session.refresh(base_maker)
            return base_maker
    except Exception as e:
        RuntimeError(e)


async def update_base_marker(id: int, model: schemas.BaseMarkerBase):
    try:
       async with AsyncSession(engine_async) as session:
            query = select(models.BaseMarker).where(models.BaseMarker.id == id)
            result = await session.exec(query)
            base_marker = result.one()
            if base_marker:
                base_marker.name = model.name
                base_marker.description = model.description
                base_marker.options = model.options
                base_marker.template_id = model.template_id
                await session.commit()
                await session.refresh(base_marker)
                return base_marker
            else:
                return None
    except Exception as e:
        RuntimeError(e)


async def delete_base_marker(id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.BaseMarker).where(models.BaseMarker.id == id)
            result = await session.exec(query)
            base_marker = result.one()
            await session.delete(base_marker)
            await session.commit()
            return base_marker
    except Exception as e:
        RuntimeError(e)


async def exists(id: int):
    base_marker = await get_base_marker_by_id(id)
    return True if base_marker else False
