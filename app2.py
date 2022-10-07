# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from modules import calc

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

def windowedFigure(windowSize, service):
    df = calc.apiDataFrame(service, windowSize=windowSize)
    fig = px.bar(df, x="date", y="counts")
    return fig

app.layout = html.Div([
    
    html.Div(children=[
    html.H1(children='LME 검색엔진 사용량(더미 테스트)'),

    html.Div(children='''
        Window Size (일간/주간/월간)
    '''),
    dcc.Dropdown(
        id='window1',
        options = ['daily','weekly','monthly'],
        value = 'daily'
    ),
    dcc.Graph(
        id='graph1',
        figure = windowedFigure('daily', 'lme_search')
    )],
style={'width':'45%', 'float':'left'}),

    html.Div(children=[
    html.H1(children='KITECH API 사용량'),

    html.Div(children='''
        Window Size (일간/주간/월간)
    '''),
    dcc.Dropdown(
        id='window2',
        options = ['daily','weekly','monthly'],
        value = 'daily'
    ),
    dcc.Graph(
        id='graph2',
        figure = windowedFigure('daily', 'kitech_api')
    )],
style={'width':'45%', 'float':'right', 'margin':(0,0,0,0)})

])
@app.callback(
    Output("graph1","figure"),
    Input("window1","value")    
)
def updateLME(window):
    figure = windowedFigure(window, 'lme_search')
    return figure

@app.callback(
    Output("graph2","figure"),
    Input("window2","value")    
)
def updateKITECH(window):
    figure = windowedFigure(window, 'kitech_api')
    return figure

if __name__ == '__main__':
    app.run_server(debug=True, port=3002)