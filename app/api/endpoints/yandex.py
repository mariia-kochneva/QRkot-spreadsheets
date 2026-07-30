from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.core.yandex_client import get_yandex_client, YandexDiskClient
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
)
async def generate_report(
    session: AsyncSession = Depends(get_async_session),
    yandex_client: YandexDiskClient = Depends(get_yandex_client),
) -> str:
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )

    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет закрытых проектов для формирования отчёта.',
        )

    projects_data = [
        {
            'name': project.name,
            'duration': (
                project.close_date - project.create_date
                if project.close_date and project.create_date
                else None
            ),
            'description': project.description,
        }
        for project in projects
    ]

    try:
        public_url = await create_simple_report(projects_data, yandex_client)
        return public_url
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при создании отчёта: {str(e)}',
        )
