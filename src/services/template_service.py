import glob
import os
import uuid
from typing import Union
import pandas as pd
from fastapi import HTTPException

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DataError, SQLAlchemyError, NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from tqdm import tqdm

from core.models import models
from core.models.database import engine_async
from core.schemas import schemas
from services import placeholder_service
from services.input_service import cast_templates

DOWNLOADS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'downloads')


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


async def  get_template_by_id(template_id: str):
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


async def exists(template_id: str):
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


async def download_templates_csv(n=50000, mode='exhaustive', template_id=None):

    if n is None:
        n = 50000

    if mode is None:
        mode = 'exhaustive'

    try:
        async with AsyncSession(engine_async) as session:
            result = []

            if template_id:
                template = await get_template_by_id(template_id)
                if not template:
                    raise HTTPException(status_code=404, detail="Template not found")

                templates = cast_templates(template)
            else:
                templates = cast_templates(await get_all_templates())

            templates_build = [t.build_csv(n=n, mode=mode) for t in templates]

            for r in tqdm(templates_build, desc='Generating CSV', total=len(templates_build)):
                template_id = r[0]

                template = await get_template_by_id(template_id)
                expected_result = template[0].expected_result

                builds = r[1]

                oracle_type = ''

                if 'ex' in template_id.lower():
                    oracle_type = 'three_reasos'
                elif 'yn' in template_id.lower():
                    oracle_type = 'yes_no'
                elif 'wh' in template_id.lower():
                   oracle_type = 'wh_question'
                elif 'mc' in template_id.lower():
                    oracle_type = 'mc'

                for b in builds:
                    placeholders = b[0]
                    build = b[1]
                    csv_template_data = {
                        'template_id': template_id,
                        'number_placeholders': len(placeholders)-1,
                    }

                    group_keys = [key for key in placeholders.keys() if "group" in key.lower()]

                    for i, group_key in enumerate(group_keys, start=1):
                        csv_template_data[f'group_{i}'] = placeholders[group_key]

                    csv_template_data['biased_statement'] = placeholders['[bias_statement]']
                    csv_template_data['prompt'] = build
                    csv_template_data['oracle_type'] = oracle_type
                    csv_template_data['expected_result'] = expected_result

                    result.append(csv_template_data)

            max_groups = max(
                (len([key for key in r.keys() if key.startswith('group_')]) for r in result),
                default=0
            )

            for r in result:
                for i in range(1, max_groups + 1):
                    if f'group_{i}' not in r:
                        r[f'group_{i}'] = None

                non_group_keys = {key: r[key] for key in r if not key.startswith('group_')}
                group_keys = {key: r[key] for key in r if key.startswith('group_')}

                ordered_dict = {
                    'template_id': non_group_keys.get('template_id'),
                    'number_placeholders': non_group_keys.get('number_placeholders'),
                    **dict(sorted(group_keys.items(), key=lambda x: int(x[0].split('_')[1]))),  # Ordenar group_n
                    'biased_statement': non_group_keys.get('biased_statement'),
                    'prompt': non_group_keys.get('prompt'),
                    'oracle_type': non_group_keys.get('oracle_type'),
                    'expected_result': non_group_keys.get('expected_result'),
                }

                r.clear()
                r.update(ordered_dict)

            df = pd.DataFrame(result)


            csv_path = os.path.join(DOWNLOADS_FOLDER, f'template-{uuid.uuid4()}.csv')
            df.to_csv(csv_path, sep=';', index=False)


            return csv_path

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # def _placeholder_in(template, generated):
    #
    #     _result = []
    #
    #     for placeholder in template.placeholders:
    #         pi = [p for p in placeholder.values if p.strip().lower() in generated.strip().lower()]
    #         _result.extend(list(set(pi)))
    #
    #     return _result
    #
    # try:
    #     _clean_downloads_folder()
    #     templates = await get_all_templates()
    #     if not templates:
    #         raise HTTPException(status_code=404, detail="No templates found")
    #
    #     for template in templates:
    #         id = template.id
    #         template = schemas.Template(**template.dict())
    #         generated = template.build(mode='exhaustive')[0]
    #
    #         for g in generated:
    #             csv_template_data = {
    #                 'template_id': id,
    #                 'template_base': template.base,
    #                 'placeholders': '',
    #                 'expected_result': template.expected_result,
    #                 'generated_text': ''
    #             }
    #             placeholders = _placeholder_in(template, g)
    #             l = len([p for p in template.placeholders])
    #             placeholders = _remove_substrings([p.lower() for p in placeholders], l)
    #             csv_template_data['placeholders'] = '//'.join(placeholders)
    #             csv_template_data['generated_text'] = g
    #             result.append(csv_template_data)
    #
    #     csv_data = pd.DataFrame(result)
    #
    #     file_name = os.path.join(DOWNLOADS_FOLDER, f'template-{uuid.uuid4()}.csv')
    #     csv_data.to_csv(file_name, index=False)
    #
    #     return file_name
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


def _clean_downloads_folder():
    files = glob.glob(os.path.join(DOWNLOADS_FOLDER, '*'))

    if len(files) > 10:
        files.sort(key=os.path.getctime)

        for file in files[:len(files) - 10]:
            os.remove(file)


def _remove_substrings(groups, l):

    if len(groups) == l:
        return groups
    groups.sort(key=len, reverse=True)

    result = []
    for i, group in enumerate(groups):
        if not any(group in other for other in groups[:i]):
            result.append(group)
    return result
