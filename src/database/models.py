import enum

from sqlalchemy import Enum, Index
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VaultType(enum.Enum):
    GOOGLE_DRIVE = 1
    LOCAL = 2


class DocumentInfo(Base):
    __tablename__ = 'document_info'
    __table_args__ = (Index('identifier_index', "vault_id", "vault_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    vault_id: Mapped[str]
    name: Mapped[str]
    vault_type: Mapped[VaultType] = mapped_column(Enum(VaultType))
    path: Mapped[str]
    create_date = mapped_column(DATETIME)
    update_date = mapped_column(DATETIME)
