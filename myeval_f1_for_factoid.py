# Created by LEO at the night of 2022/06/28
# Because of the dump script inherited i can not understand

import re
import argparse
import json
import sys
import csv
import string
from collections import Counter


import MeCab
def remecab(word):
    word = word.split(' ')
    mecab = MeCab.Tagger('-r /dev/null -d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd -Owakati')
    return mecab.parse(''.join(word)).strip('').split()

def compute_f1(gold_toks, pred_toks):
    #gold_toks = get_tokens(a_gold)
    #pred_toks = get_tokens(a_pred)
    common = Counter(gold_toks) & Counter(pred_toks)
    print(f'common: {common}')
    num_same = sum(common.values())
    if len(gold_toks) == 0 or len(pred_toks) == 0:
        return int(gold_toks == pred_toks)
    if num_same == 0:
        return 0
    #print(num_same)
    #print(len(pred_toks))
    precision = 1.0 * num_same / len(pred_toks)
    recall = 1.0 * num_same / len(gold_toks)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'input the file'
    )
    parser.add_argument('--result_file', help='Dataset File')
    args = parser.parse_args()

    with open(args.result_file,encoding='utf-8') as test:
        dataset_csv = csv.DictReader(test)

        #gold_toks = []
        #pred_toks = []
        toks = [] #[[gold_toks, pred_toks]]

        for row in dataset_csv:
            ans = row['answer']
            pred = row['factoid_mbert']
            ans = remecab(ans)
            pred = remecab(pred)
            if not ans: ans = ['']
            if not pred: pred = ['']
            # print(normalize_answer(ans),normalize_answer(pred))
            toks.append([ans, pred])

    print(toks)

    f1_total = []
    for i,tok in enumerate(toks):
        f1_total.append(compute_f1(tok[0], tok[1]))

    print(f1_total)
    counter = Counter(f1_total)
    print(f'EM: {counter[1.0]}')
    f1 = sum(f1_total) / len(f1_total)

    print(f'F1: {f1}')