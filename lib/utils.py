from pprint import pprint
import csv

class BlockInfo:
    """
    ブロックのid, 名前, 開始サイクル、終了サイクルを格納するクラス
    """

    def __init__(self, id, type, name, peinfo, rate, cycle):
        self.id = id
        self.type = type
        self.name = name
        self.peinfo = peinfo
        self.rate = rate
        self.cycle = cycle
        self.start = 0
        self.end = 0

    def __str__(self):
        return str(self.id) + "::" + str(self.name) + ": core-" + str(self.peinfo) + ", cycle: " + str(self.cycle)

    def raw(self):
        return [
            self.id,
            self.name,
            self.peinfo,
            self.start,
            self.end
        ]

    def print_raw(self):
        pprint({
            "id"  : self.id,
            "type": self.type,
            "name": self.name,
            "peinfo": self.peinfo,
            "rate": self.rate,
            "cycle": self.cycle,
            "start": self.start,
            "end": self.end,
            "adjacent": self.adjacent.data()
        })

    # 次のブロックが存在するかどうか
    def has_next(self):
        return self.adjacent and not self.adjacent.is_empty()

    #
    def set_adjacent(self, adjacent):
        self.adjacent = adjacent

    def set_time(self, start, end = None):
        if start and self.start <= start:
            self.start = start
            if end and self.end <= end:
                self.end = end

class Stack:
    """
    実行順序決定に使うようのスタック
    """

    def __init__(self):
        self.stack = []

    def pop(self):
        if self.stack:
            return self.stack.pop()
        else:
            return None

    def append(self, data):
        if isinstance(data, list):
            self.stack.extend(data)
        else:
            self.stack.append(data)

    def data(self):
        return self.stack

    def is_empty(self):
        return len(self.stack) == 0

    def shift(self):
        if self.stack:
            return self.stack.pop(0)
        else:
            return None

    # イテレーター用宣言。next()は下記
    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i == len(self.stack):
            raise StopIteration()
        value = self.stack[self._i]
        self._i += 1
        return value

class Exporter:
    """
    CSVで出力する
    """

    def to_csv(self, filename, header, body):
        with open(filename, "w") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(body)
