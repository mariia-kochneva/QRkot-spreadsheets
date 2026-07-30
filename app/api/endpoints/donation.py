from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.models.user import User
from app.schemas.donation import (
    DonationCreate, DonationDB, DonationFullInfoDB,
)
from app.services.investment_service import InvestmentService


router = APIRouter(prefix="/donation", tags=["donations"])


@router.get(
    "/",
    response_model=list[DonationFullInfoDB],
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    service = InvestmentService(session)
    return await service.get_all_donations()


@router.post("/", response_model=DonationDB, response_model_exclude_none=True)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    service = InvestmentService(session)
    return await service.create_donation(donation, user)


@router.get("/my", response_model=list[DonationDB])
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    service = InvestmentService(session)
    return await service.get_user_donations(user)
