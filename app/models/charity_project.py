from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import (
    MIN_NAME_LENGTH,
    MAX_NAME_LENGTH,
    MIN_DESCRIPTION_LENGTH,
)
from app.models.base import InvestmentBase


class CharityProject(InvestmentBase):
    __tablename__ = 'charityproject'

    name: Mapped[str] = mapped_column(
        String(MAX_NAME_LENGTH), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            f"LENGTH(name) >= {MIN_NAME_LENGTH}",
            name="check_name_min_length"
        ),
        CheckConstraint(
            f"LENGTH(name) <= {MAX_NAME_LENGTH}",
            name="check_name_max_length"
        ),
        CheckConstraint(
            f"LENGTH(description) >= {MIN_DESCRIPTION_LENGTH}",
            name="check_description_min_length"
        ),
    )
