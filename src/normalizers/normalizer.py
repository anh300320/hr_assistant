from abc import ABC, abstractmethod


class Normalizer(ABC):
    @abstractmethod
    def normalize(self, tokens: list[str]):
        raise NotImplementedError


class NormalizeChain:
    def __init__(
            self,
            normalizers: list[Normalizer],
    ):
        self._normalizers = normalizers

    def pass_through(self, tokens: list[str]) -> list[str]:
        for normalizer in self._normalizers:
            tokens = normalizer.normalize(tokens)
        return tokens


class ToLowerCase(Normalizer):
    def normalize(self, tokens: list[str]) -> list[str]:
        normalized_tokens = []
        for token in tokens:
            normalized_tokens.append(token.lower())
        return normalized_tokens


class TokenRefiner(Normalizer):

    def __init__(
            self,
            config,
    ):
        self._supported_langs = config['supported_langs']
        self._dictionary_filepaths = []
        for lang in self._supported_langs:
            self._dictionary_filepaths.append(config['dictionary_tmpl'].format(lang=lang))

    def normalize(self, tokens: list[str]):
        for dictionary_fp in self._dictionary_filepaths:
            self._normalize_with_dictionary(dictionary_fp)

    def _normalize_with_dictionary(self, dictionary_fp: str):
        all_words = set()
        with open(dictionary_fp) as fd:
            for word in fd.readlines():
                word = word.strip()
