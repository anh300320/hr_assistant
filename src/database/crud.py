import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from src.common.objects import Metadata, VaultType
from src.database import models
from src.database.connection import get_db
from src.database.models import DocumentInfo, TrackedFolder
from sqlalchemy import select


def add_document_metadata(session: Session, metadatas: List[Metadata]) -> List[DocumentInfo]:
    # db = SessionLocal()
    batch = []
    for metadata in metadatas:
        obj = DocumentInfo(
            name=metadata.name,
            vault_id=metadata.vault_id,
            vault_type=models.VaultType(metadata.vault_type.value),
            path=metadata.link,
            create_date=metadata.update_date,
            update_date=metadata.create_date,
        )
        batch.append(obj)
    session.add_all(batch)
    session.flush()
    for obj in batch:
        session.refresh(obj)
    logging.getLogger(__name__).info(
        "Inserted %s metadatas to db",
        len(batch)
    )
    return batch


def load_all_metadatas(
        vault_type: int,
        batch_size: int = 1000,
) -> List[DocumentInfo]:
    page = 0
    with get_db() as db:
        while True:
            stmt = select(DocumentInfo)\
                .where(DocumentInfo.vault_type == models.VaultType(vault_type))\
                .limit(batch_size)\
                .offset(page * batch_size)
            rows = db.execute(stmt)
            if not rows:
                break
            yield rows # TODO convert
            page += 1

def get_document(
        vault_id: str,
        vault_type: VaultType,
) -> Optional[DocumentInfo]:
    with get_db(auto_commit=False) as db:
        stmt = (
            select(DocumentInfo)
            .where(
                DocumentInfo.vault_type == models.VaultType(vault_type.value),
                DocumentInfo.vault_id == vault_id
            )
        )
        row = db.execute(stmt).scalars().first()
        return row


def get_doc_by_id(
        doc_id: int
) -> DocumentInfo:
    with get_db(auto_commit=False) as db:
        stmt = (
            select(DocumentInfo)
            .where(
                DocumentInfo.id == doc_id
            )
        )
        row = db.execute(stmt).scalars().first()
        return row


def batch_update_docs_update_time(
        session: Session,
        metadatas: List[Tuple[DocumentInfo, Metadata]],
):
    session.bulk_update_mappings(
        DocumentInfo,
        [
            {'id': d.id, 'update_date': m.update_date} for d, m in metadatas
        ]
    )
    session.flush()


def add_tracked_folder(folder: Metadata):
    with get_db() as db:
        tracked_folder = TrackedFolder(
            name=folder.name,
            vault_id=folder.vault_id,
            vault_type=models.VaultType(folder.vault_type.value),
            path=folder.link,
            create_date=folder.update_date,
            update_date=folder.create_date,
        )
        db.add(tracked_folder)
        db.flush()
        db.commit()
        logging.getLogger(__name__).info(
            "Added tracked folder %s", folder.name
        )
