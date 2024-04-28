import json
import re

if __name__ == '__main__':
    raw_fp = "../resources/words.txt"
    data_fp = "../resources/vie.dictionary"
    unique_words = set()
    with open(raw_fp, 'r', encoding='utf-8') as fd:
        lines = []
        for line in fd.readlines():
            # lines.append(line)
            word_info = json.loads(line)
            word = word_info['text']
            for w in word.split(' '):
                w = re.sub(r'[\()*\s\n\.\"\',;]', '', w)
                if w and '-' not in w:
                    unique_words.add(w.lower())
    with open(data_fp, 'w', encoding='utf-8') as fd:
        for w in unique_words:
            fd.write(f'{w}\n')
