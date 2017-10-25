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

## Requirements
- python3.6.2

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
- 行き先がなくなるまで繰り返すが、UnitDelayの場合は行き先があるけれど終了になることがあるので、終了条件にUnitdelayであるかどうかも追加する。行き着いたブロックがUnitDelayで有る場合は、次の操作に移るという操作を加える。
- ベース周期を取得したので、周期だけの配列を取得してそれをユニークにして、`> 0`の値のみを取り出す。[0.1, 0.2, 0.3]の場合、周期は[0.1, 0.2, 0.3, 0.6]の4種類分の周期表がいる。存在する周期から何通りあるかを確認するメソッドを作る。あとはその回数だけループをまわす。周期はベースレートの定数倍である必要があるという制約を加える。
- コア間通信をsetting.yamlに入力して、それを実際に使う。
- UnitDelayの対応。最初はperformance[task]の時間実行されるが、二回目はperformance[update]で実行されるらしい
- 無限ループのような構造は ↑ UnitDelayがからんでいるので、この処理を適切に行わないと無限ループに陥ってしまうかも。
- サブシステム内のブロックを全て展開して考える。実行順序を決定後サブシステム内のブロックの最小startTime ~ 最大endTimeをサブシステムのstartTime ~ endTimeとする。peifoはNoneのままにして、それに対応した色づけを行う。
