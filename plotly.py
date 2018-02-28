from lib import plotly as Plotly

if __name__ == "__main__":
    plot = Plotly.Plotly("./outputs/fibo.csv", { "showTitle": False })
    #plot = Plotly.Plotly([
    #    "./outputs/output_rate_0.csv",
    #    "./outputs/output_rate_1.csv"
    #])
    plot.plot()
