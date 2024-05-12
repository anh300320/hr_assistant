import dataclasses
import json
import logging
from collections import defaultdict
from typing import List

from lsm import LSM

from src.common.objects import Index, Reference


class IndexPersistent:

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
        with LSM(self._index_fp) as db:
            for key, refs in index.index.items():
                val = self._convert_to_str_value(refs)
                current_val = ""
                if key in db:
                    current_val = db[key]
                db[key] = ",".join([current_val, val])

    def _convert_to_str_value(
            self,
            references: List[Reference]
    ) -> str:
        values = []
        for ref in references:
            values.append(f"{ref.document_id}|{ref.position}")
        return ",".join(values)
