# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from modules import calc

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

def windowedFigure(windowSize):
    df = calc.apiDataFrame('lme_search',windowSize=windowSize)
    fig = px.bar(df, x="date", y="counts")
    return fig

app.layout = html.Div(children=[
    html.H1(children='LME 검색엔진 사용량(더미 테스트)'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),
    dcc.Dropdown(
        id='window',
        options = ['daily','weekly','monthly'],
        value = 'daily'
    ),
    dcc.Graph(
        id='graph',
        figure = windowedFigure('daily')
    )
])

@app.callback(
    Output("graph","figure"),
    Input("window","value")    
)
def update_bar_chart(window):
    figure = windowedFigure(window)
    return figure

if __name__ == '__main__':
    app.run_server(debug=True, port=3002)