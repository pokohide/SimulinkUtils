from lib import flow_decider as FD
from lib import graph_manager as GM

if __name__ == "__main__":
    gm = GM.GraphManager("./perf.xml")
    gm.run()
    print(gm.base_rate)
    fd = FD.FlowDecider(gm.startBlockName, gm.blockTable)
    fd.run()
    fd.to_csv("hoge.csv")
