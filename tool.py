import argparse
import json
import csv

def load_data(filename):
    output = []
    with open(filename, "r", encoding='utf-8') as reader:
        input_data = json.load(reader)
        for i in input_data.keys():
            output.append({'model_answer': input_data[i]})
    return output

def write2csv(data, filename, header):
    with open(filename, 'w', encoding='utf-8',  newline='') as fo:
        writer = csv.DictWriter(fo, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

def write2json_cebkr(data, filename):
    if filename[-1].isalnum():
        filename += '/'
    for k, v in data.items():
        with open(filename + k + '.json', 'w', encoding='utf-8') as fo:
            json.dump(v, fo, ensure_ascii=False)

def write2json(data, filename):
    with open(filename, 'w', encoding='utf-8') as fo:
        json.dump(data, fo, ensure_ascii=False)

def load_data_fromcsv(filename):
    output = {
        'a_cut': [],
        'q_cut': [],
        'both_cut': [],
        'neither_cut': []
    }
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        i = 1
        for row in reader:
            if int(row['USE']) == 1:
                exp_acut = {'qid' : i,
                        'question': row['Question_O'].replace('\n', '').replace(' ', ''),
                        'context': row['Context'].replace('\n', '').replace(' ', ''),
                        'answer': '',
                        'answer_start': 0,
                        'title': i,
                        'is_impossible': False}
                exp_qcut = {'qid' : i,
                        'question': row['Question'].replace('\n', '').replace(' ', ''),
                        'context': row['Context_O'].replace('\n', '').replace(' ', ''),
                        'answer': '',
                        'answer_start': 0,
                        'title': i,
                        'is_impossible': False}
                exp_bcut = {'qid' : i,
                        'question': row['Question'].replace('\n', '').replace(' ', ''),
                        'context': row['Context'].replace('\n', '').replace(' ', ''),
                        'answer': '',
                        'answer_start': 0,
                        'title': i,
                        'is_impossible': False}
                exp_ncut = {'qid' : i,
                        'question': row['Question_O'].replace('\n', '').replace(' ', ''),
                        'context': row['Context_O'].replace('\n', '').replace(' ', ''),
                        'answer': '',
                        'answer_start': 0,
                        'title': i,
                        'is_impossible': False}

                i += 1
                output['a_cut'].append(exp_acut)
                output['q_cut'].append(exp_qcut)
                output['both_cut'].append(exp_bcut)
                output['neither_cut'].append(exp_ncut)
            else:
                continue

    for k, v in output.items():
        output[k] = {'dataset': 'test', 'data':v}
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str)
    parser.add_argument('--output', type=str)
    parser.add_argument('--op', type=str)
    args = parser.parse_args()
    if args.op == 'r':
        data = load_data(args.input)
        write2csv(data, args.output, ['model_answer'])
    elif args.op == 'w':
        output = load_data_fromcsv(args.input)
        write2json_cebkr(output, args.output)
