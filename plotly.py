from lib import plotly as Plotly

if __name__ == "__main__":
    # plot = Plotly.Plotly("./examples/tmp_sch_results.csv", { "showTitle": False })
    plot = Plotly.Plotly([
        "./outputs/output_rate_0.csv",
        "./outputs/output_rate_1.csv"
    ])
    plot.plot()
