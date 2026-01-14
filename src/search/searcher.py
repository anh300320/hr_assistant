from src.search.boolean_search import parse_raw_boolean_search, BooleanSearch, Operator
from src.search.entry_processor import EntryProcessor
from src.search.retriever import Retriever


class Searcher:
    def __init__(
        self,
        retriever: Retriever,
        entry_processor: EntryProcessor,
    ):
        self._retriever = retriever
        self._entry_processor = entry_processor

    def search(self, query: str) -> list[int]:
        raise NotImplementedError

    def _query(self, query: str) -> set[int]:
        entries = self._entry_processor.produce_search_entries(query)
        result = set()
        for entry in entries:
            matched_doc_ids = self._retriever.get(entry)
            result = result.union(matched_doc_ids)
        return result


class BooleanSearcher(Searcher):
    def __init__(
        self,
        retriever: Retriever,
        entry_processor: EntryProcessor,
    ):
        super().__init__(retriever, entry_processor)

    def search(self, query: str) -> list[int]:
        boolean_query = parse_raw_boolean_search(query)
        return list(self._execute_search(boolean_query))

    def _execute_search(self, boolean_search: BooleanSearch) -> set[int]:
        if isinstance(boolean_search.value, str):
            return self._query(boolean_search.value)
        else:
            left_result = self._execute_search(boolean_search.left)
            right_result = self._execute_search(boolean_search.right)
            if boolean_search.value == Operator.OR:
                return left_result.union(right_result)
            else:
                return left_result.intersection(right_result)
