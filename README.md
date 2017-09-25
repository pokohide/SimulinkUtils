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
pip install pyyaml
pip install plotly
python main.py # 実行
```

## Usage
`setting.yaml.example`を元に`setting.yaml`を作成する


## TODO
- ベース周期を取得したので、周期だけの配列を取得してそれをユニークにして、`> 0`の値のみを取り出す。[0.1, 0.2, 0.3]の場合、周期は[0.1, 0.2, 0.3, 0.6]の4種類分の周期表がいる。存在する周期から何通りあるかを確認するメソッドを作る。あとはその回数だけループをまわす。周期はベースレートの定数倍である必要があるという制約を加える。
- コア間通信をsetting.yamlに入力して、それを実際に使う。
