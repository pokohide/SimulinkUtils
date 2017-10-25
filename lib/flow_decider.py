from . import utils as Utils

class FlowDecider:
    """
    与えられたブロックごとに実行順序と実行サイクルの近接リストから
    実行順序を決定するモジュール。
    show: https://paper.dropbox.com/doc/iNWxqRTxmCzgRouRWcoLY
    """

    def __init__(self, startBlocks, blockTable):
        self.startBlocks = startBlocks
        self.blockTable = blockTable
        self.stack = Utils.Stack()
        self.results = {}
        self.maxEndTime = 0.0

    def run(self):
        for start in self.startBlocks:
            while(True):
                if self._calculate_time(start.name): break
        print("done")
        # self._print(self.blockTable)

    def to_csv(self, filename):
        "結果をCSV出力"
        exporter = Utils.Exporter()
        exporter.to_csv(filename, self._csv_header(), self._csv_body())

    def _calculate_time(self, target):
        "開始ブロックから次のブロックまでのサイクル数などを計算する"
        block = self.blockTable[target]

        # block.is_unitdelay()の時はupdateを加算する?
        startTime, endTime = block.start, block.start + block.performance["task"]
        block.set_time(startTime, endTime)
        if self.maxEndTime < endTime: self.maxEndTime = endTime

        # ブロックが合流地点だった場合
        if block.is_confluence():
            self.stack.sorted("code")
            nextBlock = self.stack.pop()
            if nextBlock is None: return True
            nextBlockName = nextBlock.get("name")
            self.blockTable[nextBlockName].add_settled(target)
            if block.peinfo == self.blockTable[nextBlockName].peinfo:
                self.blockTable[nextBlockName].set_time(startTime)
            return self._calculate_time(nextBlockName)

        # 次のブロックがあるとき
        if block.has_next():
            block.next.sorted("code")
            for nextSet in block.next:
                nextBlock = self.blockTable[nextSet.get("name")]
                "次のブロックに今のブロックの終了時刻と次のブロックまでの移動コストを開始時刻として設定する"
                nextBlock.set_time(endTime + nextSet.get("cycle"))

            nextBlock = block.next.shift()
            nextBlockName = nextBlock.get("name")
            self.blockTable[nextBlockName].add_settled(target)
            self.stack.append(block.next.data())

            "行き先ブロックと割当コアが変わったときはスタック上の同じ割当コアのブロックのstartTimeを変更する"
            if block.peinfo != self.blockTable[nextBlockName].peinfo:
                for stack in self.stack.data():
                    stack_block = self.blockTable[stack.get("name")]
                    if block.peinfo == stack_block.peinfo: stack_block.set_time(endTime)

            return self._calculate_time(nextBlockName)
        else:
            importer = self.stack.pop()
            if importer is None: return True
            importerName = importer.get("name")
            self.blockTable[importerName].add_settled(target)
            return self._calculate_time(importerName)

    # 開始ブロック名を与えればそこから計算する。再帰関数
    # def _calculate_time(self, target):
    #     block = self.blockTable[target]
    #     startTime = block.start
    #     endTime = startTime + block.performance["task"]
    #     if self.maxEndTime < endTime: self.maxEndTime = endTime
    #
    #     block.set_time(startTime, endTime)
    #
    #     if block.has_next():
    #         for nextSet in block.next:
    #             nextBlock = self.blockTable[nextSet[0]]
    #             nextBlock.set_time(endTime)
    #
    #         nextBlock = block.next.shift()
    #         self.stack.append(block.next.data())
    #         return self._calculate_time(nextBlock[0])
    #
    #     else:
    #         importer = self.stack.pop()
    #         if importer == None: return True
    #         return self._calculate_time(importer[0])

    def _csv_header(self):
        return [len(self.blockTable), self.maxEndTime]
        # return ["id", "name", "peinfo", "rate", "startTime", "endTime"]

    def _csv_body(self):
        body = []
        for k in sorted(self.blockTable, key=lambda k: int(self.blockTable[k].id)):
            body.append(self.blockTable[k].raw())
        return body

    def _print(self, dict):
        for k in sorted(dict, key=lambda k: int(dict[k].id)):
            dict[k].print_raw()
