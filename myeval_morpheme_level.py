import re
import argparse
import json
import sys
import csv
import string
from collections import Counter


# mod from org normalize_answer(s)
def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        # return text.lower()
        return text

    # return white_space_fix(remove_articles(remove_punc(lower(s))))
    # mod_s = white_space_fix(remove_articles(remove_punc(lower(s))))

    # スペースは削除させない
    mod_s = remove_articles(remove_punc(lower(s)))
    return mod_s
    # return mod_s.replace(" ", "")


# mod from org f1_score()
# 引数にcontextを追加，contextの中で，predictionの形態素の位置が，ground_truthの形態素の位置と一致しているかどうかも考慮
def f1_score(prediction, ground_truth, context):
    # prediction_tokens = normalize_answer(prediction).split()
    # ground_truth_tokens = normalize_answer(ground_truth).split()

    # そもそも正解が含まれていないコンテキストの場合（大規模機械読解のタスクで起きる状況，普通の機械読解ではありえない）
    if ground_truth not in context:
        return 0

    # 形態素にsplit
    ground_truth = ground_truth.split()
    prediction = prediction.split()
    context = context.split()
    ground_truth_tokens = list(map(lambda x: x, ground_truth))
    prediction_tokens = list(map(lambda x: x, prediction))
    context_tokens = list(map(lambda x: x, context))

    # ground_truth（参照用回答）の形態素がcontextの中にある位置のインデックスのリストを作成
    ground_truth_position_list = []
    for i in range(len(context_tokens)):
        is_ground_truth_start = False
        for j in range(len(ground_truth_tokens)):  # iからi+jまですべての形態素が一致した場合，開始位置と判定
            if context_tokens[i + j] == ground_truth_tokens[j]:
                is_ground_truth_start = True
            else:
                is_ground_truth_start = False
                break

        if is_ground_truth_start:
            for j in range(len(ground_truth_tokens)):  # iからi+jまですべてのインデックスをリストに入れる
                ground_truth_position_list.append(i + j)

            break

    # prediction（モデル回答）の形態素がcontextの中にある位置のインデックスのリストを作成
    prediction_position_list = []
    for i in range(len(context_tokens)):
        is_prediction_start = False
        for j in range(len(prediction_tokens)):  # iからi+jまですべての形態素が一致した場合，開始位置と判定
            if context_tokens[i + j] == prediction_tokens[j]:
                is_prediction_start = True
            else:
                is_prediction_start = False
                break

        if is_prediction_start:
            for j in range(len(prediction_tokens)):  # iからi+jまですべてのインデックスをリストに入れる
                prediction_position_list.append(i + j)

            break

    # print(ground_truth_position_list)
    # print(prediction_position_list)

    # 位置が一致している形態素をカウント
    num_same = 0
    for pred_position in prediction_position_list:
        if pred_position in ground_truth_position_list:
            num_same += 1

    # print(num_same)

    # common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    # num_same = sum(common.values())

    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)

    # print(f1,">>>>>>>",prediction_tokens, ground_truth_tokens)
    return f1


# 引数にcontextを追加するが，使わない
def exact_match_score(prediction, ground_truth, context):
    # print(">>>>>>>",prediction, ground_truth)
    # スペースをなくしてから判定
    prediction = ''.join(prediction.split())
    ground_truth = ''.join(ground_truth.split())
    # print('prediction: ' + prediction)
    # print('ground: ' + ground_truth)
    # print(prediction == ground_truth)
    return prediction == ground_truth


# not use
def metric_max_over_ground_truths(metric_fn, prediction, ground_truths):
    scores_for_ground_truths = []
    for ground_truth in ground_truths:
        score = metric_fn(prediction, ground_truth)
        scores_for_ground_truths.append(score)
    return max(scores_for_ground_truths)


# 引数にcontextを追加
def my_metric_max_over_ground_truths(metric_fn, prediction, ground_truths, context):
    scores_for_ground_truths = []
    # for ground_truth in ground_truths:
    #    score = metric_fn(prediction, ground_truth)
    #    scores_for_ground_truths.append(score)

    score = metric_fn(prediction, ground_truths, context)
    scores_for_ground_truths.append(score)

    return max(scores_for_ground_truths)


# not use
def evaluate(dataset, predictions):
    f1 = exact_match = total = 0
    for article in dataset:
        for paragraph in article['paragraphs']:
            for qa in paragraph['qas']:
                total += 1
                if qa['id'] not in predictions:
                    message = 'Unanswered question ' + qa['id'] + \
                              ' will receive score 0.'
                    print(message, file=sys.stderr)
                    continue
                ground_truths = list(map(lambda x: x['text'], qa['answers']))
                prediction = predictions[qa['id']]
                exact_match += metric_max_over_ground_truths(
                    exact_match_score, prediction, ground_truths)
                f1 += metric_max_over_ground_truths(
                    f1_score, prediction, ground_truths)

    exact_match = 100.0 * exact_match / total
    f1 = 100.0 * f1 / total

    return {'exact_match': exact_match, 'f1': f1}


def myevaluate(dataset):
    f1 = exact_match = total = 0
    total_wa = exact_match_wa = 0

    for data in dataset:
        total += 1
        ground_truths = data[0]
        prediction = data[1]
        context = data[2]  # コンテキストも取り出す

        if ground_truths != "":
            total_wa += 1
            exact_match_wa += my_metric_max_over_ground_truths(exact_match_score, prediction, ground_truths, context)

        # print(ground_truths)
        # print(prediction)

        exact_match += my_metric_max_over_ground_truths(exact_match_score, prediction, ground_truths, context)
        f1 += my_metric_max_over_ground_truths(f1_score, prediction, ground_truths, context)
        # print(exact_match,f1)

    exact_match_ = exact_match / total
    exact_match_wa_ = exact_match_wa / total_wa
    f1_wa = f1 / total_wa
    f1_ = f1 / total

    print("EM =", exact_match_, "(", exact_match, "/", total, ")")
    print("F1 =", f1_)
    print("EM_wa =", exact_match_wa_, "(", exact_match_wa, "/", total_wa, ")")
    print("F1_wa =", f1_wa)

    return {'exact_match': exact_match, 'f1': f1}


if __name__ == '__main__':
    expected_version = '1.1'
    parser = argparse.ArgumentParser(
        description='Evaluation for TipsQA ' + expected_version)
    parser.add_argument('--result_file', help='Dataset file')

    # parser.add_argument('prediction_file', help='Prediction File')
    args = parser.parse_args()
    sample_lists = []

    # with open('./result.csv', encoding='utf-8') as testset_file:
    with open(args.result_file, encoding='utf-8') as testset_file:
        # dataset_json = json.load(dataset_file)
        # dataset = dataset_json['data']
        dataset_csv = csv.DictReader(testset_file)

        for row in dataset_csv:
            sample_list = []
            ans = row['answer']
            pred = row['model_answer']
            con = row['context']  # 位置情報を獲得するために，コンテキストも取り出す
            # print(normalize_answer(ans),normalize_answer(pred))
            sample_list.append(normalize_answer(ans))
            sample_list.append(normalize_answer(pred))
            sample_list.append(normalize_answer(con))  # ノーマルライズしてリストの3番目に入れる
            # sample_list.append(ans)
            # sample_list.append(pred)
            # print(sample_list)
            sample_lists.append(sample_list)
        # print(sample_lists)
        # print(len(sample_lists))

    myevaluate(sample_lists)
