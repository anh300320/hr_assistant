import dataclasses
import json
import logging
from collections import defaultdict

from src.common.objects import Reference


class IndexPersistent:

    def __init__(self, config):
        self._index_fp = config['index_fp']

    def persist(
            self,
            index: dict[str, list[Reference]],
    ):
        converted = self._convert_all_to_dict(index)
        self._save_to_file(converted)

    def _save_to_file(
            self,
            converted: dict[str, list[dict]],
    ):
        logging.getLogger(__name__).info(
            'Saving file to %s',
            self._index_fp
        )
        json.dump(self._index_fp)

    def _convert_all_to_dict(
            self,
            index: dict[str, list[Reference]],
    ) -> dict[str, list[dict]]:
        converted_to_dict = defaultdict(list)
        for key, refs in index.items():
            for ref in refs:
                convert = {
                    'metadata': dataclasses.asdict(ref.metadata),
                    'position': ref.position,
                }
                converted_to_dict[key].append(convert)
        return converted_to_dict
