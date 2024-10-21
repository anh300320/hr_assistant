import enum

from sqlalchemy import Enum, Index, String
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedColumn


class Base(DeclarativeBase):
    pass


class VaultType(enum.Enum):
    GOOGLE_DRIVE = 1
    LOCAL = 2


class DocumentInfo(Base):
    __tablename__ = 'document_info'
    # __table_args__ = (Index('identifier_index', "vault_id", "vault_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    vault_id: MappedColumn[str] = mapped_column(String, nullable=False)
    name: MappedColumn[str] = mapped_column(String,  nullable=False)
    vault_type: Mapped[VaultType] = mapped_column(Enum(VaultType))
    path: MappedColumn[str] = mapped_column(String, nullable=False)
    create_date = mapped_column(DATETIME)
    update_date = mapped_column(DATETIME)


class TrackedFolder(Base):
    __tablename__ = "tracked_folder"
    id: Mapped[int] = mapped_column(primary_key=True)
    vault_id: MappedColumn[str] = mapped_column(String, nullable=False)
    name: MappedColumn[str] = mapped_column(String, nullable=False)
    vault_type: Mapped[VaultType] = mapped_column(Enum(VaultType))
    path: MappedColumn[str] = mapped_column(String, nullable=False)
    create_date = mapped_column(DATETIME)
    update_date = mapped_column(DATETIME)
