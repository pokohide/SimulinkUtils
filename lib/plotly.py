import csv
import matplotlib.pyplot as plt
import utils as Utils
plt.rcParams.update({ 'font.size': 15 }) # フォントサイズ変更
plt.style.use('bmh')

class Plotly:
    """
    棒グラフを表示する
    """

    def __init__(self, fname):
        self.data = self._load_csv(fname)
        self._ax = plt.gca()

    def plot(self):
        COLORS = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

        for i in range(len(COLORS)):
            r, g, b = COLORS[i]
            COLORS[i] = (r / 255., g / 255., b / 255.)

        for item in self.data:
            core = item[0]
            data = item[1].data()
            xs = list(map(lambda x: (x["start"], x["end"] - x["start"]), data))
            colors = list(map(lambda x: "red", data))
            colors = [COLORS[i % 20] for (i, x) in enumerate(data)]
            # hatches = [("//", "\\\\")[i % 2] for (i, x) in enumerate(data)]
            self._hatch_broken_bar(xs, (core * 1.5 + 1, 1), facecolors=colors)
        self._ax.set_ylim(0, 1.5 * self.max_core + 1.5 + 0.5)
        self._ax.set_xlim(0, self.endtime)
        self._ax.set_yticks([(i * 1.5 + 1.0) for i in range(self.max_core + 1)])
        # self._ax.set_yticks([1, 2.5, 4, 5.5])
        self._ax.set_yticklabels(["core 0", "core 1", "core 2", "core 3"])
        # self._ax.set_xlabel("seconds since start")
        self._ax.grid(True)
        plt.show()

    def _hatch_broken_bar(self, xs, y, **kw):
        hatches = kw.pop("hatches", [None] * len(xs))
        facecolors = kw.pop("facecolors", [None] * len(xs))
        edgecolors = kw.pop("edgecolors", [None] * len(xs))

        for i, x in enumerate(xs):
            self._ax.barh(bottom = y[0], width = x[1], height = y[1], left = x[0],
                    facecolor = facecolors[i], edgecolor = edgecolors[i], hatch = hatches[i])

    def _load_csv(self, fname):
        cores = {}
        self.max_core = 0
        try:
            with open(fname, newline="", encoding="utf-8") as f:
                csv_reader = csv.reader(f, delimiter=",", quotechar='"')
                next(csv_reader)          # コメント行は無視
                header = next(csv_reader) # ヘッダー
                next(csv_reader)          # コメント行は無視
                self.endtime = float(header[1])
                for row in csv_reader:
                    core_num = int(row[2]) # コア数: 0 ~ x (x > 0)
                    if self.max_core < core_num: self.max_core = core_num
                    if core_num not in cores: cores[core_num] = Utils.Stack()
                    cores[core_num].append(self._format(row))
        except FileNotFoundError as e: print(e)
        except csv.Error as e: print(e)
        for core in cores.values(): core.sorted("start") # startTimeでソート

        return sorted(cores.items())

    def _format(self, data):
        """格納する配列データを整形する"""
        return {
            "id"   : int(data[0] or 0),
            "name" : data[1],
            "core" : int(data[2] or 0),
            "start": float(data[3] or 0),
            "end"  : float(data[4] or 0)
        }

if __name__ == "__main__":
    # plot = Plotly("./examples/adddelay_singlerate_sensorless.csv")
    plot = Plotly("./examples/adddelay_singlerate_sensorless_100us.csv")
    # plot = Plotly("./examples/singlerate_100us.csv")
    # plot = Plotly("./examples/singlerate.csv")
    # plot = Plotly("./examples/sample.csv")
    plot.plot()
