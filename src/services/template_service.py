from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas


async def get_all_templates():
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template, models.BaseMarker, models.CompositeMarker).join(models.BaseMarker, isouter=True).join(models.CompositeMarker, isouter=True)
            result = await session.exec(query)
            return await _transform_results_to_template_retrieve(result.unique().all())
        
    except Exception as e:
        print(e)


async def get_template_by_id(id: int):
    try:
        async with AsyncSession(engine_async) as session:
            query = select(models.Template, models.BaseMarker, models.CompositeMarker).join(models.BaseMarker, isouter=True).join(models.CompositeMarker, isouter=True).where(models.Template.id == id)
            result = await session.exec(query)
            return await _transform_results_to_template_retrieve(result.unique().all())

    except Exception as e:
        print(e)


async def create_template(model: schemas.TemplateCreate):
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
        print(e)


async def update_template(id: int, model: schemas.TemplateUpdate):
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
    for template, base_marker, composite_marker in result:

        if template.id not in templates_dict:
            templates_dict[template.id] = schemas.TemplateRetrieve(
                id=template.id,
                base=template.base,
                description=template.description,
                base_markers=[],
                composite_markers=[]  
            )

        if base_marker:
            base_marker_retrieve = schemas.BaseMarkerRetrieve(
                id=base_marker.id,
                name=base_marker.name,
                description=base_marker.description,
                options=base_marker.options,
                template_id=base_marker.template_id
            )
            
            if base_marker_retrieve not in templates_dict[template.id].base_markers:
                templates_dict[template.id].base_markers.append(base_marker_retrieve)

        if composite_marker:
            composite_marker_retrieve = schemas.CompositeMarkerRetrieve(
                id=composite_marker.id,
                options=composite_marker.options,
                template_id=composite_marker.template_id
            )
            if composite_marker_retrieve not in templates_dict[template.id].composite_markers:
                templates_dict[template.id].composite_markers.append(composite_marker_retrieve)

    return list(templates_dict.values())
