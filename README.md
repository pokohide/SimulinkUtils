## Configuration

このファイルは以下の要素で構成されいます。
- `GraphManager`
- `FlowDecider`

### GraphManager

与えられたコア割当情報付きBLXMLから[id, name, peinfo, rate, performance]などを抽出し、
ブロック間のつながりを`output`の情報を元に隣接リストを生成するクラス。

隣接リストはコア間通信性能とブロックの処理性能を足し合わせて処理サイクルを重みとして持つ。

### FlowDecider
GraphManagerから受け取った重み付き隣接リストを深さ優先探索で走査する。
この走査によって、各ブロックの開始/終了サイクルを決める。

## Requirements
- python3

## Getting Started

```
git clone hogehoge & cd hogehoge
pip install -r requirements.txt
python main.py # 実行
```

## Usage
`setting.yaml.example`を元に`setting.yaml`を作成する

```
cp setting.yaml.example setting.yaml
vim setting.yaml # 適宜修正
```

## Hot to Test

```
python -m unittest discover tests
```

## TODO
- ベース周期を取得したので、周期だけの配列を取得してそれをユニークにして、`> 0`の値のみを取り出す。[0.1, 0.2, 0.3]の場合、周期は[0.1, 0.2, 0.3, 0.6]の4種類分の周期表がいる。存在する周期から何通りあるかを確認するメソッドを作る。あとはその回数だけループをまわす。周期はベースレートの定数倍である必要があるという制約を加える。
- コア間通信をsetting.yamlに入力して、それを実際に使う。
- UnitDelayの対応。最初はperformance[task]の時間実行されるが、二回目はperformance[update]で実行されるらしい
- 無限ループのような構造は ↑ UnitDelayがからんでいるので、この処理を適切に行わないと無限ループに陥ってしまうかも。
- サブシステム内のブロックを全て展開して考える。実行順序を決定後サブシステム内のブロックの最小startTime ~ 最大endTimeをサブシステムのstartTime ~ endTimeとする。peifoはNoneのままにして、それに対応した色づけを行う。
- startBlocksは複数あるが、別コアなら同時スタート。同じコアならcodeのline番号の小さい順にする。
- Stackも基本的には先入れ先だしではなく、codeのline番号でソートする？

### Plotly
- BrokenBarに文字を追加したい
http://matplotlib.org/examples/pylab_examples/broken_barh.html
https://stackoverflow.com/questions/44706151/how-to-hatch-broken-barh-on-matplotlib-python
http://www.randalolson.com/2014/06/28/how-to-make-beautiful-data-visualizations-in-python-with-matplotlib/
http://matplotlib.org/examples/pylab_examples/barchart_demo2.html
