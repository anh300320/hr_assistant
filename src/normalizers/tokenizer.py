from nltk import wordpunct_tokenize

from src.common.objects import Token


class Tokenizer:
    def tokenize(self, text: str) -> list[Token]:
        words = wordpunct_tokenize(text)
        tokens = self._convert_words_to_tokens(words)
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
                        text=w,
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

    def _convert_words_to_tokens(
            self,
            words: list[str],
    ) -> list[Token]:
        tokens: list[Token] = []
        for i, word in enumerate(words):
            tokens.append(
                Token(
                    text=word,
                    position=i,
                )
            )
        return tokens
