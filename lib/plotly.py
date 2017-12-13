import csv
import matplotlib.pyplot as plt
from . import utils as Utils
plt.rcParams.update({ 'font.size': 15 }) # フォントサイズ変更
plt.style.use('bmh')

class Plotly:
    """
    棒グラフを表示する
    """
    HEIGHT = 1.0

    def __init__(self, fname, config = None):
        self.endtime = 0
        self.csvs = self._load(fname)
        count = len(self.csvs)

        self._fig, self._ax = plt.subplots(count, 1)
        if count is 1: self._ax = [self._ax]
        self._annotations = [[] for i in range(count)]
        self._init_colors()
        self._set_config(config)

    def plot(self):
        for index, csv in enumerate(self.csvs):
            self._set_graph(index, csv)
        self._fig.canvas.mpl_connect('button_press_event', self._on_press)
        self._fig.tight_layout()
        plt.show()

    def _set_graph(self, index, csv):
        for item in csv:
            core = item[0]
            data = item[1].data()
            xs = list(map(lambda x: (x["start"], x["end"] - x["start"]), data))
            colors = self._set_colors(data)
            self._hatch_broken_bar(index, xs, (core * 1.5 + 1, 1), facecolors=colors)
            for block in data:
                width, annotation = self._get_annotation(index, block)
                self._annotations[index].append((width, annotation))

        if self.config.get("showTitle", False):
            self._ax[index].set_title(self.fnames[index], { "fontsize": 10 })
        self._ax[index].set_ylim(0, 1.5 * self.max_core + 1.5 + self.__class__.HEIGHT / 2)
        self._ax[index].set_xlim(0, self.endtime)
        self._ax[index].set_yticks([(i * 1.5 + self.__class__.HEIGHT) for i in range(self.max_core + 1)])
        self._ax[index].set_yticklabels([("core " + str(i)) for i in range(self.max_core + 1)])
        self._ax[index].grid(True)

    def _on_press(self, event):
        visibility_changed = False
        index = 0
        for i, ax in enumerate(self._ax):
            if ax == event.inaxes: index = i

        x, y = event.xdata, event.ydata
        for width, annotation in self._annotations[index]:
            should_be_visible = self._is_contain(annotation.xy, width, self.__class__.HEIGHT, x, y)

            if should_be_visible != annotation.get_visible():
                visibility_changed = True
                annotation.set_visible(should_be_visible)
        if visibility_changed: plt.draw()

    def _is_contain(self, txy, width, height, x, y):
        """
        ターゲットのxyとそのwidth, heightを渡す。その長方形の中にx, yが含まれているかを返す
        """
        tx, ty = txy
        dx = abs(tx - x)
        dy = abs(ty - y)
        return (dx < width / 2) and (dy < height / 2)

    def _get_annotation(self, index, block):
        """
        ブロックのホバー時にブロック名を表示する
        """
        width = block["end"] - block["start"]
        x = block["start"] + width / 2.0
        y = block["core"] * 1.5 + 1
        annotation = self._ax[index].annotate(
            block["name"], xy = (x, y), xycoords="data",
            xytext=(x + 10, y + self.__class__.HEIGHT / 2), textcoords="data",
            bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.9),
            arrowprops=dict(arrowstyle="->", connectionstyle='arc3,rad=0.3', facecolor='black', edgecolor="black")
            )
        annotation.set_visible(False)
        return (width, annotation)

    def _hatch_broken_bar(self, index, xs, y, **kw):
        hatches = kw.pop("hatches", [None] * len(xs))
        facecolors = kw.pop("facecolors", [None] * len(xs))
        edgecolors = kw.pop("edgecolors", [None] * len(xs))

        for i, x in enumerate(xs):
            self._ax[index].barh(bottom = y[0], width = x[1], height = y[1], left = x[0],
                    facecolor = facecolors[i], edgecolor = edgecolors[i], hatch = hatches[i])

    def _load(self, fnames):
        if isinstance(fnames, list):
            self.fnames = fnames
            csvs = []
            for fname in fnames:
                csv = self._load_csv(fname)
                csvs.append(csv)
            return csvs
        elif isinstance(fnames, str):
            self.fnames = [fnames]
            return [self._load_csv(fnames)]

    def _load_csv(self, fname):
        cores = {}
        self.max_core = 0
        try:
            with open(fname, newline="", encoding="utf-8") as f:
                csv_reader = csv.reader(f, delimiter=",", quotechar='"')
                next(csv_reader)          # コメント行は無視
                header = next(csv_reader) # ヘッダー
                next(csv_reader)          # コメント行は無視
                if self.endtime < float(header[1]): self.endtime = float(header[1])
                for row in csv_reader:
                    core_num = int(row[2]) # コア数: 0 ~ x (x > 0)
                    if self.max_core < core_num: self.max_core = core_num
                    if core_num not in cores: cores[core_num] = Utils.Stack()
                    cores[core_num].append(self._format(row))
        except FileNotFoundError as e: print(e)
        except csv.Error as e: print(e)
        for core in cores.values(): core.sorted("start") # startTimeでソート

        return sorted(cores.items())

    def _set_colors(self, data):
        colors = []
        for block in data:
            block_id = block['id']
            color = self.color_table.get(block_id, None)
            if color is None:
                color = self.colors[self.color_index % len(self.colors)]
                self.color_table[block_id] = color
                self.color_index += 1
            colors.append(color)
        return colors

    def _set_config(self, config):
        if config is None:
            self.config = { "showTitle": True }
        else:
            self.config = config

    def _init_colors(self):
        def to_rgb(color):
            r, g, b = color
            return (r / 255., g / 255., b / 255.)
        COLORS = [(255, 185, 0), (231, 72, 86), (0, 120, 215), (0, 153, 188), (122, 117, 116), (118, 118, 118),
            (255, 140, 0), (232, 17, 35), (0, 99, 177), (45, 125, 154), (93, 90, 88), (76, 74, 72),
            (247, 99, 12), (234, 0, 94), (142, 140, 216), (0, 183, 195), (104, 118, 138), (105, 121, 126),
            (202, 80, 16), (195, 0, 82), (107, 105, 214), (3, 131, 135), (81, 92, 107), (74, 84, 89),
            (218, 59, 1), (227, 0, 140), (135, 100, 184), (0, 178, 148), (86, 124, 115), (100, 124, 100),
            (239, 105, 80), (191, 0, 119), (116, 77, 169), (1, 133, 116), (72, 104, 96), (82, 94, 84),
            (209, 52, 56), (194, 57, 179), (177, 70, 194), (0, 204, 106), (73, 130, 5), (132, 117, 69),
            (255, 67, 67), (154, 0, 137), (136, 23, 152), (16, 137, 62), (16, 124, 16), (126, 115, 95)]
        #
        # COLORS = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
        #      (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
        #      (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
        #      (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
        #      (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

        self.colors = list(map(lambda color: to_rgb(color), COLORS ))
        self.color_table = {}
        self.color_index = 0

    def _format(self, data):
        """格納する配列データを整形する"""
        return {
            "id"   : int(data[0] or 0),
            "name" : data[1],
            "core" : int(data[2] or 0),
            "start": float(data[3] or 0),
            "end"  : float(data[4] or 0)
        }
