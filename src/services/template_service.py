from typing import Union

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas


async def get_all_templates():
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template, models.BaseMarker).join(models.BaseMarker, isouter=True)
            result = await session.exec(query)
            return await _transform_results_to_template_retrieve(result.unique().all())
        
    except Exception as e:
        print(e)


async def get_template_by_id(id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template, models.BaseMarker).join(models.BaseMarker, isouter=True).join(isouter=True).where(models.Template.id == id)
            result = await session.exec(query)
            return await _transform_results_to_template_retrieve(result.unique().all())

    except Exception as e:
        print(e)


async def create_template(model: Union[schemas.TemplateCreateMarker, schemas.TemplateBase]):
    if 'markers' not in model.dict() or not model.markers:
        return await create_template_without_markers(model)
    else:
        return await create_template_with_markers(model)


async def create_template_without_markers(model: schemas.TemplateBase):
    template: models.Template = models.Template(
        base=model.base,
        description=model.description,
    )
    try:
        async with AsyncSession(engine_async) as session:
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template
    except Exception as e:
        raise e


async def create_template_with_markers(model: schemas.TemplateCreateMarker):
    template: models.Template = models.Template(
        base=model.base,
        description=model.description,
    )
    try:
        template_retrieve: schemas.TemplateRetrieve = schemas.TemplateRetrieve(
            id=0,
            base=template.base,
            description=template.description,
            markers=[]
        )
        async with AsyncSession(engine_async) as session:
            session.add(template)
            await session.commit()
            await session.refresh(template)
            template_retrieve.id = template.id
            print(template_retrieve)
            for marker in model.markers:
                base_marker = models.BaseMarker(
                    name=marker.name,
                    description=marker.description,
                    options=marker.options,
                    template_id=template.id
                )
                print(base_marker)
                session.add(base_marker)
                await session.commit()
                await session.refresh(base_marker)
                template_retrieve.markers.append(schemas.BaseMarkerRetrieve(
                    id=base_marker.id,
                    name=base_marker.name,
                    description=base_marker.description,
                    options=base_marker.options,
                    template_id=base_marker.template_id
                ))
            return template_retrieve
    except Exception as e:
        raise e


async def update_template(id: int, model: schemas.TemplateBase):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template).where(models.Template.id == id)
            result = await session.exec(query)
            template = result.one()
            template.base = model.base
            template.description = model.description
            await session.commit()
            await session.refresh(template)
            return await get_template_by_id(id)
    except Exception as e:
        print(e)


async def delete_template(id: int):
    try:
        async with AsyncSession(engine_async) as session:
            template = await session.get(models.Template, id)
            await session.delete(template)
            await session.commit()
            return template
    except Exception as e:
        print(e)


async def exists(id: int):
    template = await get_template_by_id(id)
    template = template[0] if template else None
    return True if template else False


async def _transform_results_to_template_retrieve(result):
    templates_dict = {}

    if not result:
        return []
    for template, base_marker in result:

        if template.id not in templates_dict:
            templates_dict[template.id] = schemas.TemplateRetrieve(
                id=template.id,
                base=template.base,
                description=template.description,
                markers=[]
            )

        if base_marker:
            base_marker_retrieve = schemas.BaseMarkerRetrieve(
                id=base_marker.id,
                name=base_marker.name,
                description=base_marker.description,
                options=base_marker.options,
                template_id=base_marker.template_id
            )
            
            if base_marker_retrieve not in templates_dict[template.id].markers:
                templates_dict[template.id].markers.append(base_marker_retrieve)

    return list(templates_dict.values())
