## Configuration

このファイルは以下の要素で構成されいます。
- `GraphManager`
- `FlowDecider`
- `Plotly`

### GraphManager

与えられたコア割当情報付きBLXMLから[id, name, peinfo, rate, performance]などを抽出し、
ブロック間のつながりを`output`の情報を元に隣接リストを生成するクラス。

隣接リストはコア間通信性能とブロックの処理性能を足し合わせて処理サイクルを重みとして持つ。

### FlowDecider
GraphManagerから受け取った重み付き隣接リストを深さ優先探索で走査する。
この走査によって、各ブロックの開始/終了サイクルを決める。

やっていることは以下の通り
1. 開始ブロックから深さ優先で探索を開始する。
2. 行き先が分岐している場合は、各ブロックのコードが記述されている行数を確認して小さい順から走査する。
3. ブロックが合流の場合は、スタックに保持されているブロックから探索を再スタートする。
4. 以下2 ~ 3を行き先がなくなるまで繰り返す。

### Plotly
各ブロックごとの開始・終了サイクルが記載されたcsvファイルを読み込んで、ガントチャートを表示するツール。
FlowDeciderによって出力されるcsvファイルやbltmp2cでコア割当時に生成されるtmp_sch_results.csvが使える。

#### Plotlyの実行方法

`plotly.py`を参考に.

```
from lib import plotly as Plotly

# source = "example.csv"
# source = ["example1.csv", "example2.csv"]
options = { "showTitle": False }

plotly = Plotly.Plotly(source, options)
plotly.plot()
```

## Requirements
- python3.6.2

## Getting Started

```
git clone https://github.com/nu-manycore/Lab.git & cd Lab/FlowVisualizer
pip install -r requirements.txt
# settings.ymlを編集
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
- 周期は現状1, 2といった整数倍に限る。0.002といった少数には対応していないので、一番小さな周期を整数に正規化する処理をはさむ。
