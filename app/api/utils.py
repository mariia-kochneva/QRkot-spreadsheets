from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud


async def get_project_or_404(project_id: int, session: AsyncSession):
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Проект не найден!"
        )
    return project
