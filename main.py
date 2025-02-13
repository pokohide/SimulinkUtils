from lib import flow_decider as FD
from lib import graph_manager as GM
from lib import plotly as Plotly
from lib import utils as Utils

if __name__ == "__main__":
    yl = Utils.YamlLoader('setting.yaml')

    gm = GM.GraphManager(yl.get("input", "input.xml"))
    gm.run()

    fd = FD.FlowDecider(gm.startBlocks, gm.blockTable, gm.maxRate)
    fd.run()

    if yl.get("plot", False):
        plotly = Plotly.Plotly(fd.files)
        plotly.plot()
