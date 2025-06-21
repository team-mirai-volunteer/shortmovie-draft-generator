from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import current_timestamp
from typing import Optional
from datetime import datetime

from src.lib.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=current_timestamp())
    last_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=current_timestamp(), server_default=current_timestamp())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name}, email={self.email}, created_at={self.created_at}, last_updated_at={self.last_updated_at})>"

    def __str__(self) -> str:
        return f"User(id={self.id}, name={self.name}, email={self.email}, created_at={self.created_at}, last_updated_at={self.last_updated_at})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at,
            "last_updated_at": self.last_updated_at,
        }
