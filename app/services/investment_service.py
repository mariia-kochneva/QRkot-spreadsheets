from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.charity_project import CharityProject
from app.models.donation import Donation
from app.models.user import User
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate
)
from app.schemas.donation import DonationCreate


class InvestmentService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(
            self, project_data: CharityProjectCreate
    ) -> CharityProject:
        await self._validate_name_duplicate(project_data.name)
        new_project = await charity_project_crud.create(
            project_data, self.session
        )
        await self._invest(new_project)
        await self.session.commit()
        await self.session.refresh(new_project)
        return new_project

    async def update_project(
        self, project: CharityProject, update_data: CharityProjectUpdate
    ) -> CharityProject:
        self._validate_project_not_closed(project)
        if update_data.full_amount is not None:
            self._validate_full_amount(
                update_data.full_amount, project.invested_amount
            )
        if update_data.name is not None:
            await self._validate_name_duplicate(update_data.name)
        updated = await charity_project_crud.update(
            project, update_data, self.session
        )
        self._close_if_funded(updated)
        await self.session.commit()
        await self.session.refresh(updated)
        return updated

    async def delete_project(self, project: CharityProject) -> CharityProject:
        self._validate_no_investments(project.invested_amount)
        await charity_project_crud.remove(project, self.session)
        await self.session.commit()
        return project

    async def get_all_projects(self) -> list[CharityProject]:
        return await charity_project_crud.get_multi(self.session)

    async def create_donation(
        self, donation_data: DonationCreate, user: User
    ) -> Donation:
        new_donation = await donation_crud.create(
            donation_data, self.session, user
        )
        await self._invest(new_donation)
        await self.session.commit()
        await self.session.refresh(new_donation)
        return new_donation

    async def get_all_donations(self) -> list[Donation]:
        return await donation_crud.get_multi(self.session)

    async def get_user_donations(self, user: User) -> list[Donation]:
        return await donation_crud.get_by_user(self.session, user)

    async def _validate_name_duplicate(self, name: str) -> None:
        project_id = await charity_project_crud.get_project_id_by_name(
            name, self.session
        )
        if project_id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Проект с таким именем уже существует!",
            )

    @staticmethod
    def _validate_project_not_closed(project: CharityProject) -> None:
        if project.fully_invested:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Закрытый проект нельзя редактировать!",
            )

    @staticmethod
    def _validate_full_amount(new_amount: int, invested: int) -> None:
        if new_amount < invested:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=(
                    "Нельзя установить значение full_amount меньше"
                    " уже вложенной суммы."
                ),
            )

    @staticmethod
    def _validate_no_investments(invested_amount: int) -> None:
        if invested_amount > 0:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="В проект были внесены средства, не подлежит удалению!",
            )

    async def _invest(self, new_obj: CharityProject | Donation) -> None:
        if isinstance(new_obj, Donation):
            targets = await charity_project_crud.get_open_projects(
                self.session
            )
        else:
            targets = await donation_crud.get_open_donations(self.session)

        for target in targets:
            free = new_obj.full_amount - new_obj.invested_amount
            if free <= 0:
                break
            available = target.full_amount - target.invested_amount
            amount = min(free, available)
            target.invested_amount += amount
            new_obj.invested_amount += amount
            self._close_if_funded(target)
            self._close_if_funded(new_obj)

        self.session.add(new_obj)
        for obj in targets:
            self.session.add(obj)
        await self.session.flush()

    def _close_if_funded(self, obj) -> None:
        if obj.invested_amount >= obj.full_amount:
            obj.fully_invested = True
            obj.close_date = datetime.now(timezone.utc)
            self.session.add(obj)
