from lib import decider as D
from lib import graph_manager as GM

if __name__ == "__main__":
    gm = GM.GraphManager("./perf.xml")
    gm.run()
    decider = D.Decider(gm.startBlockName, gm.blockTable)
    decider.run()
    decider.to_csv("hoge.csv")
