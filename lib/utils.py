from pprint import pprint
import csv
import yaml

class BlockInfo:
    """
    ブロックのid, 名前, 開始サイクル、終了サイクルを格納するクラス
    """

    def __init__(self, id, type, name, peinfo, rate, offset, performance, code):
        self.id = id
        self.type = type
        self.name = name
        self.peinfo = peinfo
        self.rate = rate
        self.performance = performance
        self.code = code
        self.start = 0.0
        self.end = 0.0
        self.offset = offset
        self.next = Stack()
        self.prev = Stack()
        self.settled = set()
        # もう解析したブロック名

    def raw(self):
        return [
            self.id,
            self.name,
            self.peinfo or 0,
            # self.performance,
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
            "offset": self.offset,
            "performance": self.performance,
            "code": self.code,
            "start": self.start,
            "end": self.end,
            "next": self.next.data(),
            "prev": self.prev.data()
        })

    # 次のブロックが存在するかどうか
    def has_next(self):
        return self.next and not self.next.is_empty()

    # 前にブロックが存在するかどうか
    def has_prev(self):
        return self.prev and not self.prev.is_empty()

    # このブロックは複数ブロックから合流しているかどうか
    def is_confluence(self):
        return self.prev.length() - len(self.settled) >= 1

    # サブシステムかどうか
    def is_subsystem(self):
        return self.type and self.type == "SubSystem"

    # Constantかどうか
    def is_constant(self):
        return self.type and self.type == "Constant"

    # UnitDelayかどうか
    def is_unitdelay(self):
        return self.type and self.type == "UnitDelay"

    # UnitDelay[update]かどうか
    def is_unitdelay_update(self):
        return self.is_unitdelay() and ('[update]' in self.name)

    def set_neighbor(self, key, blocks):
        if key == "input":
            self.prev = blocks
        elif key == "output":
            self.next = blocks

    def set_time(self, start, end = None, force = False):
        if self.start <= start:
            self.start = start
            if end and self.end <= end:
                self.end = end
        if force is True:
            self.start = start
            self.end = end

    def add_settled(self, blockName):
        self.settled.add(blockName)

class Stack:
    """
    実行順序決定に使うようのスタック
    """

    def __init__(self):
        self.stack = []

    def pop(self):
        if self.stack:
            # return self.stack.pop() # 後ろからとる
            return self.stack.pop(0)
        else:
            return None

    def pop_if(self, condition):
        "条件を満たす要素を取り出す"
        if self.stack:
            for index, item in enumerate(self.stack):
                if condition(item): return self.stack.pop(index)
            return None
        else:
            return None

    def any(self, condition):
        for item in self.stack:
            if condition(item): return True
        return False

    def append(self, data):
        if isinstance(data, list):
            self.stack.extend(data)
        else:
            self.stack.append(data)

    def remove_by_name(self, name):
        new_stack = [e for e in self.stack if e.get('name') != name]
        self.stack.clear()
        self.stack.extend(new_stack)
        del new_stack

    def length(self):
        if self.stack: return len(self.stack)
        return 0

    def data(self):
        return self.stack

    def is_empty(self):
        return len(self.stack) == 0

    def shift(self):
        if self.stack:
            return self.stack.pop(0)
        else:
            return None

    def sorted(self, target):
        self.stack.sort(key=lambda x:x[target])

    def clear(self):
        self.stack.clear()

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
            # of blocks, # of connections, # maximum delay
            writer.writerow(["% # of blocks", " # of connections", " # maximum delay"])
            writer.writerow(header)
            writer.writerow(["% block no", " block name", " core", " start time", " end time"])
            writer.writerows(body)

class YamlLoader:
    """
    YAMLからデータをロードする
    """

    def __init__(self, fname):
        self.data = self._load(fname)

    def get(self, key, default = None):
        return self.data.get(key, default)

    def _load(self, fname):
        with open(fname, 'rt') as fp:
            text = fp.read()
            return yaml.safe_load(text)

class Plotly:
    """
    ガントチャートをプロットする
    """

    def __init__(self, fname):
        self.data = self._read(fname)

    def plot(self):
        print(1)

    def _read(self, fname):
        hoge = 1
