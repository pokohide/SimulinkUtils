import xml.etree.ElementTree as ET
from . import utils as Utils
import copy

class GraphManager:
    """
    SimulinkModelを記述するXMLを解析してブロックの実行順序と実行サイクルを
    抽出するモジュール。この情報をDeciderに渡すことで開始/終了サイクルを計算する。
    show: https://paper.dropbox.com/doc/iNWxqRTxmCzgRouRWcoLY
    """

    def __init__(self, input):
        self.maxRate = 0
        self.root = ET.parse(input).getroot()
        self._make_block_table()
        self.startBlocks = Utils.Stack()

    def _make_block_table(self):
        "ブロック名からidやコア数を索引できるテーブルを作成"
        self.blockTable = {}
        for block in self.root.findall(".//block"):
            name = block.get("name")
            self.blockTable[name] = self._get_block(block)

    def run(self):
        rootBlocks = self.root.findall("./block")
        self._scan_blocks(rootBlocks)
        self._set_base_rate()
        self._set_startBlocks()
        self._print(self.blockTable)

    def _scan_blocks(self, blockNodes):
        "BLXMLのブロックを解析する"
        # total_cycle = 0.0
        # peinfo = None

        for node in blockNodes:
            # ここでこのブロックが周期内かを確認。周期外であればスキップする
            # rateがない(=0)の場合もあることに注意
            name = node.get("name")
            # peinfo = peinfo or block.get("peinfo")
            # total_cycle += float(block.get(""))
            # cycle = float(block.get(""))

            if node.get("blocktype") == "SubSystem":
                for input in node.findall("./input"):
                    # 後ろのブロックを取得
                    prevBlockName = self._get_inner_block(input.find("connect"))
                    nextBlockName = input.get("port")

                    # つなぎこみ
                    self.blockTable[prevBlockName].next.append({ "name": nextBlockName, "cycle": 0.0, "code": 0 })
                    self.blockTable[nextBlockName].prev.append({ "name": prevBlockName, "cycle": 0.0, "code": 0 })

                output = node.find("./output")
                if output is not None:
                    prevBlockName = output.get("port")
                    for connect in output.findall("connect"):
                        nextBlockName = self._get_inner_block(connect)

                        # つなぎこみ
                        self.blockTable[prevBlockName].next.append({ "name": nextBlockName, "cycle": 0.0, "code": 0 })
                        self.blockTable[nextBlockName].prev.append({ "name": prevBlockName, "cycle": 0.0, "code": 0 })

                # 再帰
                smBlocks = node.findall("./sm:blocks/block", namespaces = { "sm": "http://example.com/SimulinkModel" })
                self._scan_blocks(smBlocks)
            elif node.get("blocktype") == "UnitDelay":

                blockName = node.get("name")
                updateName = blockName + '[update]'
                taskName = blockName + '[task]'

                self.blockTable[taskName] = copy.deepcopy(self.blockTable[blockName])
                self.blockTable[taskName].name = taskName

                self.blockTable[updateName] = copy.deepcopy(self.blockTable[blockName])
                self.blockTable[updateName].name = updateName

                block = self.blockTable[blockName]

                output = node.find("./output")
                if output is not None:
                    self.startBlocks.append(self.blockTable[taskName])
                    for connect in output.findall("connect"):
                        nextBlockName = self._get_inner_block(connect)
                        nextBlock = self.blockTable[nextBlockName]
                        cycle = self._calculate_cycle(block, nextBlock)

                        self.blockTable[taskName].next.append({ "name": nextBlockName, "cycle": cycle, "code": nextBlock.code["task"] })
                        self.blockTable[nextBlockName].prev.append({ "name": taskName, "cycle": cycle, "code": 0 })
                        self.blockTable[nextBlockName].prev.remove_by_name(blockName)

                for input in node.findall("./input"):
                    for connect in input.findall("connect"):
                        prevBlockName = self._get_inner_block(connect)
                        prevBlock = self.blockTable[prevBlockName]
                        cycle = self._calculate_cycle(prevBlock, block)

                        self.blockTable[updateName].prev.append({ "name": prevBlockName, "cycle": cycle, "code": prevBlock.code["task"] })
                        self.blockTable[prevBlockName].next.append({ "name": updateName, "cycle": cycle, "code": 0 })
                        self.blockTable[prevBlockName].next.remove_by_name(blockName)
            else:
                self._set_next_blocks(node)
                self._set_prev_blocks(node)

    def _get_inner_block(self, connect):
        "サブシステム内のブロック名を取得する"
        blockName = connect.get("block")
        if self.blockTable[blockName].is_subsystem():
            blockName = connect.get("port")
        return blockName

    def _set_next_blocks(self, blockNode):
        "あるブロックの次のブロックをセットする"
        blockName = blockNode.get("name")
        block = self.blockTable[blockName]
        output = blockNode.find("./output")
        if output is not None:
            for connect in output.findall("connect"):
                nextBlockName = self._get_inner_block(connect)
                nextBlock = self.blockTable[nextBlockName]
                cycle = self._calculate_cycle(block, nextBlock)
                self.blockTable[blockName].next.append({ "name": nextBlockName, "cycle": cycle, "code": nextBlock.code["task"] })

    def _set_prev_blocks(self, blockNode):
        "あるブロックの手前のブロックをセットする"
        blockName = blockNode.get("name")
        block = self.blockTable[blockName]
        for input in blockNode.findall("./input"):
            for connect in input.findall("connect"):
                prevBlockName = self._get_inner_block(connect)
                prevBlock = self.blockTable[prevBlockName]
                cycle = self._calculate_cycle(prevBlock, block)
                self.blockTable[blockName].prev.append({ "name": prevBlockName, "cycle": cycle, "code": prevBlock.code["task"] })

    def _set_startBlocks(self):
        "開始ブロックをセットする"
        for blockName, block in self.blockTable.items():
            # サブシステムでなく、次のブロックがあるが後続ブロックがない場合、そのブロックは開始ブロックである。
            if block.is_subsystem() or block.is_constant() or block.is_unitdelay(): continue # 定数やサブシステムからは開始しない
            if block.has_next() and not block.has_prev():
                self.startBlocks.append(block)

    # ベース周期を取得する
    def _set_base_rate(self):
        self.base_rate = min(self.blockTable[k].rate for k in self.blockTable)

    def _print(self, dict):
        for k in sorted(dict, key=lambda k: int(dict[k].id)):
            dict[k].print_raw()

    def _calculate_cycle(self, block, nextBlock):
        "現在のブロック名と次のブロック名から移動コスト(コア間通信)を返す。"
        if block.peinfo is None or nextBlock.peinfo is None:
            return 0.0
        if block.peinfo != nextBlock.peinfo:
            # 行き先ブロックとコアが違う場合コア間通信が発生。ここでは50とする。
            return float(50)
        return 0.0

    def _get_attr(self, block, attr):
        "ブロックから属性を抽出して整形する"
        key = "typical" if attr == "performance" else "line"
        task = block.find(".//" + attr + "[@type='task']")
        update = block.find(".//" + attr + "[@type='update']")
        init = block.find(".//" + attr + "[@type='init']")

        task = float(task.get(key)) if task is not None else 0.0
        update = float(update.get(key)) if update is not None else 0.0
        init = float(init.get(key)) if init is not None else 0.0

        return { "task": task, "update": update, "init": init }

    def _get_rate_and_offset(self, block):
        "ブロックから周期とオフセットを返す"
        try:
            rate = eval(block.get("rate"))
            if isinstance(rate, int) or isinstance(rate, float):
                rate, offset = rate, 0
            elif isinstance(rate, list):
                rate, offset = rate
        except:
            rate, offset = 0, 0
        if rate <= 0 : rate = 0
        return rate, offset

    def _get_block(self, block):
        rate, offset = self._get_rate_and_offset(block)
        if rate > self.maxRate: self.maxRate = rate
        return Utils.BlockInfo(
            block.get("id"),
            block.get("blocktype"),
            block.get("name"),
            block.get("peinfo"),
            float(rate),
            float(offset),
            self._get_attr(block, "performance"),
            self._get_attr(block, "code")
        )
