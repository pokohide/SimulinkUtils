import xml.etree.ElementTree as ET
from . import utils as Utils

class GraphManager:
    """
    SimulinkModelを記述するXMLを解析してブロックの実行順序と実行サイクルを
    抽出するモジュール。この情報をDeciderに渡すことで開始/終了サイクルを計算する。
    show: https://paper.dropbox.com/doc/iNWxqRTxmCzgRouRWcoLY
    """

    def __init__(self, input):
        self.root = ET.parse(input).getroot()
        self._make_block_table()

    # ブロック名からidやコア数などを索引できる表を作成
    def _make_block_table(self):
        self.blockTable = {}
        for block in self.root.findall(".//block"):
            name = block.get("name")
            self.blockTable[name] = self._get_block(block)

    def run(self):
        blocks = self.root.findall(".//block")
        self.startBlockName = blocks[0].get("name")

        for block in blocks:
            # ここでこのブロックが周期内かを確認。周期外であればスキップする

            blockName = block.get("name")
            adjacencyList = Utils.Stack()

            nextBlockElem = block.find(".//output")
            output = block.find(".//output")
            if output != None:
                for connect in output.findall("connect"):
                    nextBlockName = connect.get("block")
                    cycle = self._calculate_cycle(blockName, nextBlockName)
                    adjacencyList.append( (nextBlockName, cycle) )
            self.blockTable[blockName].set_adjacent(adjacencyList)

        self._set_base_rate()
        self._print(self.blockTable)

    # ベース周期を取得する
    def _set_base_rate(self):
        self.base_rate = min(self.blockTable[k].rate for k in self.blockTable)

    def _print(self, dict):
        for k in sorted(dict, key=lambda k: int(dict[k].id)):
            dict[k].print_raw()

    # 現在ブロック名と次ブロック名から実行サイクルを計算
    def _calculate_cycle(self, blockName, nextBlockName):
        block = self.blockTable.get(blockName)
        nextBlock = self.blockTable.get(nextBlockName)
        cycle = block.cycle

        if block.peinfo != nextBlock.peinfo:
            # 行き先ブロックとコアが違う場合コア間通信が発生。ここでは50とする。
            cycle += float(50)

        return cycle

    def _get_block(self, block):
        performance = block.find(".//performance[@type='task']")
        cycle = 0
        if performance != None: cycle = float(performance.get("typical"))

        return Utils.BlockInfo(
            block.get("id"),
            block.get("blocktype"),
            block.get("name"),
            block.get("peinfo"),
            float(block.get("rate")),
            cycle
        )
