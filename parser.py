import xml.etree.ElementTree as ET
import yaml
import csv

class YamlLoader:
    """設定ファイル(.yaml)をロードするLoader"""

    def __init__(self, input):
        self.input = input

    def load(self):
        with open(self.input, "r+") as f:
            text = f.read()
        # ここでエラー処理。もしなければこの形式で作成してくださいと出力
        self.data = yaml.load(text)

class Parser:
    """BLXMLをパースして欲しい情報をCSVで出力するParser"""

    def __init__(self, input, attrs = None):
        self.input = input
        # ここで指定した要素のみをcsvに出力する
        self.attrs = attrs or ["id", "name", "type", "peinfo", "rate"]
        self.infos = []

    def to_csv(self, output):
        self._load_xml()
        with open(output, "w") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(self._csv_header())
            writer.writerows(self._csv_body())

    def _load_xml(self):
        tree = ET.parse(self.input)
        root = tree.getroot()
        for block in root.findall(".//block"):
            info = self._get_attr_from_block(block)
            self.infos.append(info)

    def _get_attr_from_block(self, block):
        return {
            "id"    : block.get("id"),
            "type"  : block.get("blocktype"),
            "name"  : block.get("name"),
            "peinfo": block.get("peinfo"),
            "rate"  : block.get("rate"),
            # perfomanceはどうやって格納しよう。そもそも何が必要か
        }

    # CSVのヘッダー
    def _csv_header(self):
        return self.attrs

    # CSV出力の本体
    def _csv_body(self):
        return list(map(self._extract, self.infos))

    # 情報から必要な要素のみを抽出する
    def _extract(self, info):
        return list(map(lambda attr: info.get(attr),self.attrs))

if __name__ == "__main__":
    loader = YamlLoader("setting.yaml")
    loader.load()

    parser = Parser(loader.data["parser"]["input_file"], loader.data["parser"]["attributes"])
    parser.to_csv(loader.data["parser"]["output_file"])
