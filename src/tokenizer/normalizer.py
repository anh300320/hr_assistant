from abc import ABC, abstractmethod
from typing import List, Set

import nltk
from nltk.stem import WordNetLemmatizer
from src.common.objects import Token


class Normalizer(ABC):
    @abstractmethod
    def normalize(self, tokens: List[Token]) -> List[Token]:
        raise NotImplementedError


class LemmingNormalizer(Normalizer):
    def __init__(self):
        nltk.download('wordnet')    # TODO find away to pre-download and put it to resources
        self._lemmatizer = WordNetLemmatizer()

    def normalize(
            self,
            tokens: List[Token],
    ) -> List[Token]:

        def add_token(
                all_tokens: List[Token],
                uniq: Set[str],
                tk: Token
        ):
            if tk.text in uniq:
                return
            uniq.add(tk.text)
            all_tokens.append(tk)

        result = []
        for token in tokens:
            uniq_words = set()
            result.append(token)
            uniq_words.add(token.text)
            noun = self._lemmatizer.lemmatize(word=token.text, pos="n")
            noun_tk = Token(text=noun, position=token.position)
            verb = self._lemmatizer.lemmatize(word=token.text, pos="v")
            verb_tk = Token(text=verb, position=token.position)
            add_token(result, uniq_words, noun_tk)
            add_token(result, uniq_words, verb_tk)
        return result
