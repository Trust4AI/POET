import os
import json

from core.models import models
from core.models.database import engine_async
from sqlmodel.ext.asyncio.session import AsyncSession

TEMPLATE_DIR = './'


def list_templates():
    result = os.listdir(TEMPLATE_DIR)
    return [f for f in result if f.endswith('.json')]


async def save_template(template):
    async with AsyncSession(engine_async) as session:
        session.add(template)
        await session.commit()
        await session.refresh(template)
        return template


async def save_markers(markers):
    async with AsyncSession(engine_async) as session:
        session.add_all(markers)
        await session.commit()
        return markers


async def load_template(template_data):
    template = models.Template(
        base=template_data['base'],
        description=template_data['description'],
        expected_result=template_data['expected_result']
    )

    saved_template = await save_template(template)

    if 'markers' in template_data:
        markers = []
        for marker_data in template_data['markers']:
            marker = models.BaseMarker(
                name=marker_data['name'],
                description=marker_data['description'],
                options=marker_data['options'],
                template_id=saved_template.id
            )
            markers.append(marker)
        await save_markers(markers)


async def load_templates():
    templates = list_templates()
    for template_file in templates:
        with open(f'{TEMPLATE_DIR}{template_file}', 'r') as file:
            template_data = json.load(file)
            for single_template_data in template_data:
                await load_template(single_template_data)


if __name__ == '__main__':
    import asyncio

    asyncio.run(load_templates())
