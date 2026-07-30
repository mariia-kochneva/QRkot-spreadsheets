from sqlalchemy import Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import InvestmentBase


class Donation(InvestmentBase):
    __tablename__ = 'donation'

    comment: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user'),
        nullable=True
    )
