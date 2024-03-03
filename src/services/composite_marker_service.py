from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas


async def get_all_composite_markers():
    try:
        async with AsyncSession(engine_async) as session:
            statement = select(models.CompositeMarker)
            result = await session.exec(statement)
            return result.all()
    except Exception as e:
        print(e)


async def get_composite_marker_by_id(id: int):
    try:
        async with AsyncSession(engine_async) as session:
            statement = select(models.CompositeMarker).where(models.CompositeMarker.id == id)
            result = await session.exec(statement)
            return result.one()
    except Exception as e:
        print(e)


async def get_all_composite_markers_by_template_id(template_id: int):
    try:
        async with AsyncSession(engine_async) as session:
            statement = select(models.CompositeMarker).where(models.CompositeMarker.template_id == template_id)
            result = await session.exec(statement)
            return result.all()
    except Exception as e:
        print(e)


async def create_composite_marker(model: schemas.CompositeMarkerCreate):
    composite_maker: models.CompositeMarker = models.CompositeMarker(
        options=model.options,
        template_id=model.template_id
    )

    try:
        async with AsyncSession(engine_async) as session:
            session.add(composite_maker)
            await session.commit()
            await session.refresh(composite_maker)
            return composite_maker
    except Exception as e:
        print(e)


async def update_composite_marker(id: int, model: schemas.CompositeMarkerUpdate):
    try:
        async with AsyncSession(engine_async) as session:
            print('model', model)
            query = select(models.CompositeMarker).where(models.CompositeMarker.id == id)
            result = await session.exec(query)
            result = result.one()
            print('result', result)
            result.options = model.options 
            await session.commit()
            await session.refresh(result)
            return result
    except Exception as e:
        RuntimeError(e)


async def delete_composite_marker(id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.CompositeMarker).where(models.CompositeMarker.id == id)
            result = await session.exec(query)
            composite_marker = result.one()
            await session.delete(composite_marker)
            await session.commit()
            return composite_marker
    except Exception as e:
        RuntimeError(e)


async def exists(id: int):
    try:
        result = await get_composite_marker_by_id(id)
        print('result3', result)
        return True if result else False
    except Exception as e:
        print(e)
