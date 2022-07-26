# question-answering-evaluation
the script of question answering's evaluation such as exact match and f1, etc

## myeval_f1_ExtractiveQA.py
- 日本語抽出型・非事実型機械読解専用のEM・F1評価スクリプト（形態素単位）
- 実装環境
    - python 3.7.10（python3なら大丈夫そう）
    - mecab-ipadic-neologd https://github.com/neologd/mecab-ipadic-neologd/blob/master/README.ja.md
- 使い方
```
python myeval_f1_ExtractiveQA.py \
    --result_file = [ファイル名] 
```

    - ファイルの拡張子はcsvを定め
    - ファイルの構造:['context', 'answer', '[予測回答列のコラム名]' ]
        - '[予測回答列のコラム名]'の部分は、実際に評価したい列名に置き換える
        - スクリプトのline 85のとこにいる：`pred = row['mt5_mix']`

```
python myeval_f1_ExtractiveQA.py \
    --result_file = ./result.csv 
```
- 具体例で流れを説明
    - 具体例
        - question: `Web テスト や ES の 受付 は いつ 始まる ？` (本スクリプトとあんまり関係ないので、以後は略)
        - context: `しかし 、 Web テスト や ES の 提出 について は 日程 に 制約 は ない ため 、 早い 時期 から 実施 し て いる 企業 も あり ます 。` 
        - ground_truth(評価事例の正答): `日程 に 制約 は ない ため 、 早い 時期 から 実施 し て いる 企業 も あり ます 。`
        - pred_answer(モデルの予測回答): `早い 時期 から 実施 し て いる 企業 も あり ます`
    - 一般的に、モデルに入力したテキストは全て単語分割されたものなので、回答がコンテキストにある位置を確定しやすいため、ここで一旦前処理を行う：全ての全角・半角記号取り除き、単語をくっつける
        - context: `しかしWebテストやESの提出については日程に制約はないため早い時期から実施している企業もあります`
        - ground_truth: `日程に制約はないため早い時期から実施している企業もあります`
        - pred_answer: `早い時期から実施している企業もあります`
    - 正答と予測回答がそれぞれコンテキストにある位置を確定（ここは文字単位の位置）
        - ground_truth: [20,49]
        - pred_answer: [30,49]
        - 正答と予測の共通部分 → [30,49] → `早い時期から実施している企業もあります`
    - 形態素単位でF1値を計算するため、ここでMeCabで単語分割
        - ground_truth: `['日程', 'に', '制約', 'は', 'ない', 'ため', '早い', '時期', 'から', '実施', 'し', 'て', 'いる', '企業', 'も', 'あり', 'ます']`
        - pred_answer: `['早い', '時期', 'から', '実施', 'し', 'て', 'いる', '企業', 'も', 'あり', 'ます']`
        - 共通部分: `['早い', '時期', 'から', '実施', 'し', 'て', 'いる', '企業', 'も', 'あり', 'ます']`
    - EM = 0, PM = 1, F1 = 0.7857142857142858
        - precision = 1
        - recall = 11/17 = 0.6470
        - f1 = 2*p*r / p+r = 0.7857...
    

## myeval_f1_factoidQA.py
- 日本語事実型機械読解専用のEM・F1評価スクリプト（形態素単位）

## myeval_morpheme_level_origin.py (秘伝のタレ版)
- 形態素単位でEMとF1値を計算する
- 回答がコンテキストにいる位置は合うかどうかも考慮した
- 使い方
```
python myeval_morpheme_level.py \
    --result_file = [ファイル名] 
```
    - ファイルの拡張子はcsvを推奨
    - ファイルの構造:['context', 'answer', '[予測回答列のコラム名]' ]
```
python myeval_morpheme_level.py \
    --result_file = ./result.csv 
```

## tool.py
- 主にファイル変換用のスクリプト