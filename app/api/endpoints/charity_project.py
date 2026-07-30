from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_project_or_404
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment_service import InvestmentService


router = APIRouter(prefix="/charity_project", tags=["charity_projects"])


@router.get("/", response_model=list[CharityProjectDB])
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    service = InvestmentService(session)
    return await service.get_all_projects()


@router.post(
    "/",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    service = InvestmentService(session)
    return await service.create_project(project)


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    project = await get_project_or_404(project_id, session)
    service = InvestmentService(session)
    return await service.update_project(project, obj_in)


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    project = await get_project_or_404(project_id, session)
    service = InvestmentService(session)
    return await service.delete_project(project)
