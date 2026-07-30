from typing import TypeVar, Generic, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.base import InvestmentBase
from app.models.user import User


ModelType = TypeVar("ModelType", bound=InvestmentBase)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
        user: Optional[User] = None
    ):
        obj_in_data = obj_in.model_dump()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.flush()
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.flush()
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.flush()
        return db_obj
