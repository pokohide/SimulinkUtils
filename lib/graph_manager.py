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
        for block in self.root.findall(".//block"):
            # ここでこのブロックが周期内かを確認。周期外であればスキップする
            # rateがない(=0)の場合もあることに注意
            self._set_next_blocks(block)
            self._set_prev_blocks(block)

        self._set_base_rate()
        self._set_startBlocks()
        # print('--------------')
        #$ print(self.startBlockName)
        # self._print(self.blockTable)

    # あるブロックの次のブロックを登録する
    def _set_next_blocks(self, block):
        nextBlocks = Utils.Stack()
        blockName = block.get("name")
        output = block.find("./output")
        if output is not None:
            for connect in output.findall("connect"):
                nextBlockName = connect.get("block")
                cycle = self._calculate_cycle(blockName, nextBlockName)
                nextBlocks.append( (nextBlockName, cycle) )
        self.blockTable[blockName].set_neighbor("output", nextBlocks)

    def _set_prev_blocks(self, block):
        prevBlocks = Utils.Stack()
        blockName = block.get("name")
        for input in block.findall("./input"):
            for connect in input.findall("connect"):
                prevBlockName = connect.get("block")
                cycle = 0.0
                prevBlocks.append( (prevBlockName, cycle) )
        self.blockTable[blockName].set_neighbor("input", prevBlocks)

    def _set_startBlocks(self):
        self.startBlocks = Utils.Stack()
        for blockName, block in self.blockTable.items():
            if block.has_next() and not block.has_prev():
                # block.print_raw()
                self.startBlocks.append(blockName)

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

        if block.peinfo is None or nextBlock.peinfo is None:
            return cycle

        if block.peinfo != nextBlock.peinfo:
            # 行き先ブロックとコアが違う場合コア間通信が発生。ここでは50とする。
            cycle += float(50)

        return cycle

    def _get_block(self, block):
        performance = block.find(".//performance[@type='task']")
        cycle = 0
        if performance is not None: cycle = float(performance.get("typical"))

        return Utils.BlockInfo(
            block.get("id"),
            block.get("blocktype"),
            block.get("name"),
            block.get("peinfo"),
            float(block.get("rate") or 0),
            cycle
        )
