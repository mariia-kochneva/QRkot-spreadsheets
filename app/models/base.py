from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class InvestmentBase(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    invested_amount: Mapped[int] = mapped_column(Integer, default=0)
    fully_invested: Mapped[bool] = mapped_column(Boolean, default=False)
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    close_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
