from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas


async def get_all_base_markers():
    try:
        with AsyncSession(engine_async) as session:
            return await session.execute(models.BaseMarker.select())

    except Exception as e:
        print(e)


async def get_base_marker_by_id(id: int):
    try:
        with AsyncSession(engine_async) as session:
            return await session.execute(models.BaseMarker.select().where(models.BaseMarker.id == id))

    except Exception as e:
        print(e)


async def get_base_markers_by_template_id(template_id: int):
    try:
        with AsyncSession(engine_async) as session:
            qeury = select(models.BaseMarker).where(models.BaseMarker.template_id == template_id)
            return await session.execute(qeury)

    except Exception as e:
        print(e)


async def create_base_marker(model: schemas.BaseMarkerCreate):
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
        print(e)
