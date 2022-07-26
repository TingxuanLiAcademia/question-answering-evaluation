# Created by LEO at 2022/07/24
# 'Cuz the dump script inherited is too complicated to understand

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
    # return ''.join(mecab.parse(''.join(word)))
    return mecab.parse(''.join(word)).strip('').split()

def assemble(sentence):
    sentence = ''.join(sentence.split(' '))
    return sentence

# 文からすべての記号を消す
# 他の全角記号でもlist_double_byteに追加可能
def normalize(text):
    exclude = set(string.punctuation)
    list_double_byte = ['。','、','「','」','！','『','』','……','？','・','（','）']
    for punc in list_double_byte:
        exclude.add(punc)
    return ''.join(ch for ch in text if ch not in exclude)

# コンテキストから断片が存在するかどうかを検索する
# [start:end]で断片を確定できる
# 抽出型に対応するので、文の一部だけがコンテキストと一致することが不可能
def findSegment(context, answer): 
    pattern = answer
    string = context
    segment = re.search(pattern, string)
    if segment == None: return None
    return [segment.start(), segment.end()]

# 全部を分かち書きされる前の文を入力
# 共通する部分を確定したから，形態素解析を行う
def compute_f1_unfactoid(context, ground_truth, pred_answer):
    # 回答不可能の場合
    if ground_truth == '':
        if pred_answer == '': return 1
        else: return 0

    seg_pred = findSegment(context, pred_answer)
    if seg_pred == None: return 0
    seg_gold = findSegment(context, ground_truth)
    if seg_gold[1] <= seg_pred[0] or seg_pred[1] <= seg_gold[0]: return 0
    index_common = [seg_gold[0], seg_gold[1], seg_pred[0], seg_pred[1]]
    index_common.sort()
    common = context[index_common[1]:index_common[2]]

    common = remecab(common)
    ground_truth = remecab(ground_truth)
    pred_answer = remecab(pred_answer)
    
    num_same = len(common)
    precision = 1.0 * num_same / len(pred_answer)
    recall = 1.0 * num_same / len(ground_truth)
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

        toks = [] 

        for row in dataset_csv:
            context = row['context']
            ans = row['answer']
            pred = row['mt5_mix']
            toks.append([context, ans, pred])


    f1_total = []
    for i,tok in enumerate(toks):
        for j in [0,1,2]:
            tok[j] = normalize(tok[j]) # 記号を取り除く
            tok[j] = assemble(tok[j]) # くっつける

        # print(f'f1:{compute_f1_unfactoid(tok[0], tok[1], tok[2])}')
        f1_total.append(compute_f1_unfactoid(tok[0], tok[1], tok[2]))

    # print(f1_total)
    counter = Counter(f1_total)
    print(f'EM: {counter[1.0]}')

    count = 0
    for i in f1_total:
        if i > 0 and i < 1: count+=1
    print(f'PM: {count}')
    f1 = sum(f1_total) / len(f1_total)

    print(f'F1: {f1}')
