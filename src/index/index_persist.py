import dataclasses
import logging
from datetime import datetime
from typing import List, Optional, Iterable

from lsm import LSM

from src.common.objects import Index


@dataclasses.dataclass
class Pointer:
    doc_id: int
    position: int
    update_time: Optional[datetime]


class IndexPersistent:

    delimiter = "\n"
    DATETIME_TEMPLATE = '%Y%m%d %H%M%S'

    def __init__(self, config):
        self._index_fp = config['index_fp']

    def persist(
            self,
            index: Index,
    ):
        logging.getLogger(__name__).info(
            "Persisting %s keywords to LSM",
            len(index.index.keys())
        )
        with LSM(self._index_fp, binary=False) as db:
            for key, refs in index.index.items():
                if key in db:
                    pointers = self.parse_pointers(db[key])
                else:
                    pointers = []
                doc_id_pos_to_pointer = {}
                for pointer in pointers:
                    doc_id_pos_to_pointer[pointer.doc_id, pointer.position] = pointer
                for ref in refs:
                    doc_id_pos_to_pointer[ref.document_id, ref.position] = Pointer(
                        doc_id=ref.document_id,
                        position=ref.position,
                        update_time=ref.metadata.update_date,
                    )
                pointers = doc_id_pos_to_pointer.values()
                db[key] = self._convert_to_str_value(pointers)

    def _convert_to_str_value(
            self,
            pointers: Iterable[Pointer]
    ) -> str:
        values = []
        for pointer in pointers:
            update_date_str = "na"
            if pointer.update_time:
                update_date_str = pointer.update_time.strftime(self.DATETIME_TEMPLATE)
            values.append(f"{pointer.doc_id}|{pointer.position}|{update_date_str}")
        return self.delimiter.join(values)

    def parse_pointers(self, value: str) -> List[Pointer]:
        pointers = []
        pointers_as_str = value.split(self.delimiter)
        for s in pointers_as_str:
            try:
                values = s.split("|")
                doc_id, position, update_time_str = values
                doc_id = int(doc_id)
                position = int(position)
                update_time = None
                if update_time_str != 'na':
                    update_time = datetime.strptime(
                        update_time_str,
                        self.DATETIME_TEMPLATE,
                    )
                pointers.append(
                    Pointer(
                        doc_id=doc_id,
                        position=position,
                        update_time=update_time,
                    )
                )
            except:
                logging.getLogger(__name__).exception(
                    "Invalid pointer %s", s
                )
        return pointers
