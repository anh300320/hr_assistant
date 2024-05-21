import json
import re

def parse_v1(raw_fp, data_fp):
    unique_words = set()
    with open(raw_fp, 'r', encoding='utf-8') as fd:
        lines = []
        for line in fd.readlines():
            if 'hongocduc' not in line and 'tudientv' not in line:
                continue
            # lines.append(line)
            word_info = json.loads(line)
            word = word_info['text']
            # for w in word.split(' '):
            #     w = re.sub(r'[\()*\s\n\.\"\',;]', '', w)
            #     if w and '-' not in w:
            #         unique_words.add(w.lower())
            word = word.replace(' ', '')
            if word and '-' not in word and len(word) > 1:
                unique_words.add(word.lower())
    unique_words = list(unique_words)
    unique_words.sort(key=lambda s: len(s))
    with open(data_fp, 'w', encoding='utf-8') as fd:
        for w in unique_words:
            fd.write(f'{w}\n')

if __name__ == '__main__':
    raw_fp = "../resources/Viet22K.txt"
    data_fp = "../resources/vie.dictionary"
    words = set()
    with open(raw_fp, 'r', encoding='utf-8') as fd:
        lines = []
        for line in fd.readlines():
            for w in line.split(' '):
                w = re.sub(r'[\()*\s\n\.\"\',;]', '', w).strip()
                words.add(w.lower())
    with open(data_fp, 'w', encoding='utf-8') as fd:
        for word in words:
            if len(word) > 1:
                fd.write(f'{word}\n')
            else:
                print('x')
        fd.write("ở\n")
