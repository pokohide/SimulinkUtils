import xml.etree.ElementTree as ET
from pprint import pprint

class Decider:
    """
    実行順序を決定するクラス。
    show: https://paper.dropbox.com/doc/iNWxqRTxmCzgRouRWcoLY
    """

    def __init__(self, input):
        self.root = ET.parse(input).getroot()
        self.flow = {}   # 隣接リスト
        self._make_table()

    # ブロック名からidやコア数などを索引できる表を作成
    def _make_table(self):
        self.table = {}
        for block in self.root.findall(".//block"):
            name = block.get("name")
            self.table[name] = self._get_attr_from_block(block)

    def run(self):
        blocks = self.root.findall(".//block")
        startBlockName = blocks[0].get("name")

        for block in blocks:
            # ここでこのブロックが周期内かを確認。周期外であればスキップする

            blockName = block.get("name")
            adjacencyList = []

            for nextBlock in block.findall(".//output"):
                nextBlockName = nextBlock.find("connect").get("block")
                cycle = self._calculate_cycle(blockName, nextBlockName)

                adjacencyList.append( (nextBlockName, cycle) )

            self.flow[blockName] = adjacencyList

        print(startBlockName)
        pprint(self.flow)

    # 現在ブロック名と次ブロック名から処理サイクルを計算
    def _calculate_cycle(self, blockName, nextBlockName):
        block = self.table.get(blockName)
        nextBlock = self.table.get(nextBlockName)
        cycle = block.get("cycle")

        if block.get("peinfo") != nextBlock.get("peinfo"):
            # 行き先ブロックとコアが違う場合コア間通信が発生。ここでは50とする。
            cycle += float(50)

        return cycle

    def _get_attr_from_block(self, block):
        performance = block.find(".//performance[@type='task']")
        cycle = 0
        if performance != None: cycle = float(performance.get("typical"))

        return {
            "id"    : block.get("id"),
            "type"  : block.get("blocktype"),
            "name"  : block.get("name"),
            "peinfo": block.get("peinfo"),
            "rate"  : block.get("rate"),
            "cycle" : cycle
        }

if __name__ == "__main__":
    decider = Decider("./perf.xml")
    decider.run()
