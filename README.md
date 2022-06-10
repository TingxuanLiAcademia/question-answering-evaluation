# question-answering-evaluation
the script of question answering's evaluation such as exact match and f1, etc

## myeval_morpheme_level.py
- 形態素単位でEMとF1値を計算する
- 回答がコンテキストにいる位置は合うかどうかも考慮した
- 使い方
```
python myeval_morpheme_level.py \
    --result_file = [ファイル名] \
    --column = [予測回答列のコラム名]
```
    - ファイルの拡張子はcsvを推奨
    - ファイルの構造:['context', 'answer', '[予測回答列のコラム名]' ]
    - 例
```
python myeval_morpheme_level.py \
    --result_file = ./result.csv \
    --column = 'predictions'
```

## tool.py
- 主にファイル変換用のスクリプト