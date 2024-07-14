import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)


import json
import logging
import traceback

from sqlalchemy import text

from core.models import models
from core.models.database import engine_async
from sqlmodel.ext.asyncio.session import AsyncSession

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))


def list_templates():
    result = os.listdir(TEMPLATE_DIR)
    return [f for f in result if f.endswith('.json')]


async def save_template(template):
    try:
        async with AsyncSession(engine_async) as session:
            session.add(template)
            await session.commit()
            await session.refresh(template)
            await session.close()
            return template
    except Exception as e:
        logging.error("Failed to save template: %s\n%s", e, traceback.format_exc())
        raise


async def save_markers(markers):
    try:
        async with AsyncSession(engine_async) as session:
            session.add_all(markers)
            await session.commit()
            await session.close()
            return markers
    except Exception as e:
        logging.error("Failed to save markers: %s\n%s", e, traceback.format_exc())
        raise


async def load_template(template_data):
    try:
        template = models.Template(
            id=int(template_data['id']),
            base=template_data['base'],
            description=template_data['description'],
            expected_result=template_data['expected_result']
        )
        saved_template = await save_template(template)
        if 'placeholders' in template_data:
            markers = []
            for marker_data in template_data['placeholders']:
                marker = models.Placeholder(
                    name=marker_data['name'],
                    description=marker_data['description'],
                    values=marker_data['values'],
                    template_id=saved_template.id
                )
                markers.append(marker)
            await save_markers(markers)
    except Exception as e:
        logging.error("Failed to load template: %s\n%s", e, traceback.format_exc())
        raise


async def load_templates():
    templates = list_templates()
    for template_file in templates:
        with open(os.path.join(TEMPLATE_DIR, template_file), 'r') as file:
            template_data = json.load(file)
            if isinstance(template_data, list):
                for single_template_data in template_data:
                    await load_template(single_template_data)
            else:
                await load_template(template_data)


async def reset_database():
    async with AsyncSession(engine_async) as session:
        logging.info('Resetting database...')
        await session.exec(text("SET FOREIGN_KEY_CHECKS=0;"))
        await session.exec(text("TRUNCATE TABLE placeholder;"))
        await session.exec(text("TRUNCATE TABLE template;"))
        await session.exec(text("ALTER TABLE placeholder AUTO_INCREMENT = 1;"))
        await session.exec(text("ALTER TABLE template AUTO_INCREMENT = 1;"))
        await session.exec(text("SET FOREIGN_KEY_CHECKS=1;"))
        await session.commit()
        logging.info('Database reset successfully.')


async def main():
    logging.info('Starting the template loading process...')
    await reset_database()
    await load_templates()
    logging.info('Finished the template loading process.')


if __name__ == '__main__':
    import asyncio

    try:
        asyncio.run(main())
    except Exception as e:
        logging.error("An error occurred: %s", e)
    finally:
        logging.info("Cleanup and closing operations.")
