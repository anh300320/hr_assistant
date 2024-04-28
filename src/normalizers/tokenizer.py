from nltk import wordpunct_tokenize

Token = str


class Tokenizer:
    def tokenize(self, text: str) -> list[Token]:
        tokens = wordpunct_tokenize(text)
        new_tokens = []
        for token in tokens:
            new_tokens.extend(
                self.split_by_uppercase(token)
            )
        tokens.extend(new_tokens)

    def split_by_uppercase(self, token: str):
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
