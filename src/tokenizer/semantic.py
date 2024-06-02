import os

from src.common.objects import Token
from src.tokenizer.base import Tokenizer


class SemanticTokenize(Tokenizer):
    def __init__(self, config):
        self._supported_langs = config.get('supported_language', ['vie', 'eng'])
        self._dictionary_tmpl = config.get('dictionary_tmpl', os.path.join('resources', '{lang}.dictionary'))
        self._max_len, self._words = self._load_words()

    def tokenize(
            self,
            text: str,
    ) -> list[Token]:
        text = self._remove_all_chars_except_alnum(text)
        text = text.lower()
        return self._dp(text)

    def _dp(
            self,
            text: str,
    ):
        text = ' ' + text
        f = [len(text)] * len(text)
        trace = [-1] * len(text)
        f[0] = 0
        trace[0] = 0
        for i in range(1, len(text)):
            for j in range(self._max_len * 2):
                if i - j <= 0:
                    continue
                check_word = text[(i - j):(i + 1)]
                check_word = self._filter_out_special_char(check_word)
                if check_word in self._words:
                    if f[i-j-1] < f[i]:
                        f[i] = f[i-j-1]
                        trace[i] = i-j-1
                    elif f[i-j-1] == f[i]:
                        if not text[i - j].isalpha() or not text[i - j - 1].isalpha():
                            f[i] = f[i - j - 1]
                            trace[i] = i - j - 1
                else:
                    if f[i-j-1] + j + 1 < f[i]:
                        f[i] = f[i-j-1] + j + 1
                        trace[i] = i-j-1
        # Trace back
        tokens = []
        last_pos = len(text) - 1
        while last_pos:
            token = text[trace[last_pos] + 1: last_pos + 1]
            tokens.append(Token(self._filter_out_special_char(token), last_pos))
            last_pos = trace[last_pos]
        tokens = list(reversed(tokens))
        for i, token in enumerate(tokens):
            token.position = token.position - len(token.text)
        return tokens

    def _filter_out_special_char(self, text: str) -> str:
        text = text.lower()
        keep_only_alpha = ''
        for char in text:
            if char.isalpha():
                keep_only_alpha += char
        return keep_only_alpha

    def _load_words(self):
        max_len = 0
        words = set()
        for lang in self._supported_langs:
            fp = self._dictionary_tmpl.format(lang=lang)
            with open(fp, 'r', encoding='utf-8') as fd:
                for word in fd.readlines():
                    word = word.strip()
                    max_len = max(len(word), max_len)
                    words.add(word)
        return max_len, words
