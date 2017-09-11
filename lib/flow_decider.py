from . import utils as Utils

class FlowDecider:
    """
    与えられたブロックごとに実行順序と実行サイクルの近接リストから
    実行順序を決定するモジュール。
    show: https://paper.dropbox.com/doc/iNWxqRTxmCzgRouRWcoLY
    """

    def __init__(self, start, blockTable):
        self.start = start
        self.blockTable = blockTable
        self.stack = Utils.Stack()
        self.results = {}

    def run(self):
        while(True):
            if self._calculate_time(self.start): break
        print("done")
        # self._print(self.blockTable)

    def to_csv(self, filename):
        exporter = Utils.Exporter()
        exporter.to_csv(filename, self._csv_header(), self._csv_body())

    # 開始ブロック名を与えればそこから計算する。再帰関数
    def _calculate_time(self, target):
        block = self.blockTable[target]
        startTime = block.start
        endTime = startTime + block.cycle

        block.set_time(startTime, endTime)

        if block.has_next():
            for nextSet in block.adjacent:
                nextBlock = self.blockTable[nextSet[0]]
                nextBlock.set_time(endTime)

            nextBlock = block.adjacent.shift()
            self.stack.append(block.adjacent.data())
            return self._calculate_time(nextBlock[0])

        else:
            importer = self.stack.pop()
            if importer == None: return True
            return self._calculate_time(importer[0])

    def _csv_header(self):
        return ["id", "name", "peinfo", "rate", "startTime", "endTime"]

    def _csv_body(self):
        body = []
        for k in sorted(self.blockTable, key=lambda k: int(self.blockTable[k].id)):
            body.append(self.blockTable[k].raw())
        return body

    def _print(self, dict):
        for k in sorted(dict, key=lambda k: int(dict[k].id)):
            dict[k].print_raw()
