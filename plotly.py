from lib import plotly as Plotly

if __name__ == "__main__":
    # plot = Plotly.Plotly("./examples/adddelay_singlerate_sensorless.csv")
    # plot = Plotly("./examples/adddelay_singlerate_sensorless_100us.csv")
    # plot = Plotly("./examples/singlerate_sensorless_100us.csv")
    # plot = Plotly("./examples/singlerate_sensorless.csv")
    # plot = Plotly("./examples/sample.csv")
    plot = Plotly.Plotly("./examples/tmp_sch_results.csv")
    plot.plot()
