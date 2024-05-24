import logging
from typing import List

from src.common.objects import Metadata
from src.database import models
from src.database.connection import get_db, SessionLocal
from src.database.models import DocumentInfo


def add_document_metadata(metadatas: List[Metadata]) -> List[DocumentInfo]:
    with get_db() as db:
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
        db.add_all(batch)
        db.flush()
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
            sqlite3(DocumentInfo)\
                .filter_by(vault_type=models.VaultType(vault_type))\
                .limit(batch_size)\
                .offset(page * batch_size)
            if not rows:
                break
            yield rows # TODO convert
            page += 1
