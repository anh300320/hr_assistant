import os.path
import re

from nltk import wordpunct_tokenize

from src.common.objects import Token


class Tokenizer:
    def tokenize(self, text: str) -> list[Token]:
        text = self._remove_all_chars_except_alnum(text)
        tokens = self._extract_tokens(text)
        new_tokens = self._tokens_candidate_by_middle_uppercase(tokens)
        tokens.extend(new_tokens)
        return tokens

    def _tokens_candidate_by_middle_uppercase(
            self,
            tokens: list[Token],
    ) -> list[Token]:
        new_tokens = []
        for token in tokens:
            new_words = self._split_by_uppercase(token.text)
            for w in new_words:
                tokens.append(
                    Token(
                        text=w.lower(),
                        position=token.position,
                    )
                )
        return new_tokens

    def _split_by_uppercase(self, token: str):
        """
        Split a token if there is a upper case between it, eg: ComputerScience
        """
        length = len(token)
        # Ignore if token is capslock or has only one character
        if length == 1 or token.isupper():
            return []
        split_positions = [0]
        for i in range(1, length):
            if token[i].isupper():
                split_positions.append(i)
        split_positions.append(length)
        if len(split_positions) == 2:
            return []
        new_tokens = []
        for i in range(1, len(split_positions)):
            new_tokens.append(token[split_positions[i-1]:split_positions[i]])
        return new_tokens

    def _remove_all_chars_except_alnum(
            self,
            text: str,
    ):
        # text = re.sub(r'[^A-Za-z0-9]', ' ', text)
        normalized_text = ''
        for ch in text:
            if not ch.isalnum():
                normalized_text += ' '
            else:
                normalized_text += ch
        normalized_text = re.sub(r'\s+', ' ', normalized_text)
        return normalized_text

    def _extract_tokens(
            self,
            text: str,
    ) -> list[Token]:
        words = text.split(' ')
        tokens: list[Token] = []
        current_len = 0
        for i, word in enumerate(words):
            tokens.append(
                Token(
                    text=word.lower(),
                    position=current_len,
                )
            )
            current_len += 1 + len(word)
        return tokens
