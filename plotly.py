from lib import plotly as Plotly

if __name__ == "__main__":
    # plot = Plotly.Plotly("./examples/tmp_sch_results.csv", { "showTitle": False })
    plot = Plotly.Plotly([
        "./examples/singlerate_sensorless_100us.csv",
        "./examples/singlerate_sensorless.csv"
    ])
    plot.plot()
