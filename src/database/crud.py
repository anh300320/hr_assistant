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
