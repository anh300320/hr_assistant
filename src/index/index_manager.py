from collections import defaultdict

from src.common.objects import ParsedDocument, Reference


class IndexerManager:

    def build_index(
            self,
            documents: list[ParsedDocument],
    ) -> dict[str, list[Reference]]:
        result = defaultdict(list)
        for doc in documents:
            for token in doc.tokens:
                result[token.text].append(
                    Reference(
                        metadata=doc.metadata,
                        position=token.position,
                    )
                )
        return result
