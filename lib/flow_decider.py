from . import utils as Utils
import copy

class FlowDecider:
    """
    与えられたブロックごとに実行順序と実行サイクルの近接リストから
    実行順序を決定するモジュール。
    show: https://paper.dropbox.com/doc/iNWxqRTxmCzgRouRWcoLY
    """

    def __init__(self, startBlocks, blockTable, maxRate):
        self.startBlocksOrigin = startBlocks
        self.blockTableOrigin = blockTable
        self.blockTable = blockTable
        self.stack = Utils.Stack()
        # UnitDelayのUpdate用のスタック
        self.updateStack = Utils.Stack()
        self.results = {}
        self.maxEndTime = 0.0

        self.lapNum = 0 # 周回数
        self.maxRate = maxRate

    def run(self):
        while self.lapNum < self.maxRate:
            self.blockTable = copy.deepcopy(self.blockTableOrigin)
            self.startBlocks = copy.deepcopy(self.startBlocksOrigin)
            while (not self.startBlocks.is_empty()) or (not self.stack.is_empty()):
                start = self.startBlocks.pop()
                if start is None:
                    start = self.stack.shift()
                    startName = start.get("name")
                else:
                    startName = start.name
                while(True):
                    if self._analysis(startName, start = True): break
            self._fill_update_task()
            fname = "outputs/output_rate_" + str(self.lapNum) + ".csv"
            self.to_csv(fname)
            self.lapNum += 1
            print(self.lapNum)
        print("done")
        # self._print(self.blockTable)

    def to_csv(self, filename):
        "結果をCSV出力"
        exporter = Utils.Exporter()
        exporter.to_csv(filename, self._csv_header(), self._csv_body())

    def _analysis(self, target, start = False):
        "開始ブロックから次のブロックまでのサイクル数などを計算する"
        block = self.blockTable[target]

        startTime = block.start

        "周期と評価して、走査すべきブロックかを判定。Falseの場合は無視"
        if self._should_scan(block) is False:
            block.set_time(0.0, 0.0, force = True)
            return True

        # UnitDelay[update]は最後に空いているタイミングで行う。
        if block.is_unitdelay_update():
            self.updateStack.append(block)
            importerName = self._get_stack_block(target)
            if importerName is None: return True
            return self._analysis(importerName)

        endTime = startTime + block.performance["task"]
        block.set_time(startTime, endTime)
        if self.maxEndTime < endTime: self.maxEndTime = endTime

        # ブロックが合流地点だった場合
        if block.is_confluence(): # and start is False:
            self.stack.sorted("code")
            nextBlockName = self._get_stack_block(target, in_start = True)
            if nextBlockName is None: return True
            nextBlockInfo = self.blockTable[nextBlockName]
            if block.peinfo == nextBlockInfo.peinfo:
                shouldUpdate = False
                for settled in block.settled:
                    if block.peinfo == self.blockTable[settled].peinfo: shouldUpdate = True
                if shouldUpdate: nextBlockInfo.set_time(startTime)
            return self._analysis(nextBlockName)

        # 次のブロックがあるとき
        if block.has_next():
            block.next.sorted("code")
            "次のブロックに今のブロックの終了時刻と次のブロックまでの移動コストを開始時刻として設定する"
            for nextSet in block.next:
                nextBlockName = nextSet.get("name")
                nextBlock = self.blockTable[nextBlockName]
                nextBlock.set_time(endTime + nextSet.get("cycle"))
                self.blockTable[nextBlockName].add_settled(target)

            nextBlock = block.next.shift()
            nextBlockName = nextBlock.get("name")
            self.stack.append(block.next.data())

            "行き先ブロックと割当コアが変わったときはスタック上の同じ割当コアのブロックのstartTimeを変更する"
            if block.peinfo != self.blockTable[nextBlockName].peinfo:
                for stack in self.stack.data():
                    stack_block = self.blockTable[stack.get("name")]
                    if block.peinfo == stack_block.peinfo: stack_block.set_time(endTime)

            return self._analysis(nextBlockName)
        else:
            importerName = self._get_stack_block(target)
            if importerName is None: return True
            return self._analysis(importerName)

    def _should_scan(self, block):
        if block.rate <= 0: return False
        return (self.lapNum - block.offset) % block.rate == 0

    def _fill_update_task(self):
        "UnitDelayのupadteタスクを空いている時間に埋める"
        "とりあえずは各コアの一番遅い時間のブロックの後ろに配置する"

        for updateTask in self.updateStack:
            maxEndTime = 0
            for blockName, block in self.blockTable.items():
                if (updateTask.peinfo == block.peinfo) and (block.end > maxEndTime):
                    maxEndTime = block.end
            print(updateTask.raw())
            print(maxEndTime)
            startTime = maxEndTime
            endTime = startTime + block.performance["update"]
            block.set_time(maxEndTime, endTime, force = True)
            if self.maxEndTime < endTime: self.maxEndTime = endTime
            # print(updateTask.raw())



    def _get_stack_block(self, target = None, in_start = False):
        "次のブロックを計算時間を計算する"
        importer = self.stack.pop()
        "スタックになければ"
        if importer is None:
            if in_start:
                importer = self.startBlocks.pop()
                if importer is None: return None
                importerName = importer.name
            else:
                return None
        else:
            importerName = importer.get("name")
        if target is not None: self.blockTable[importerName].add_settled(target)
        return importerName

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
