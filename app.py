# visit http://127.0.0.1:8050/ in your web browser.

from operator import truediv
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from modules import calc

app = Dash(__name__)

# see https://plotly.com/python/px-arguments/ for more options

def windowedFigure(windowSize, service, type='usage'):
    if type == 'usage':
        df = calc.usageCount(service, windowSize=windowSize)
    elif type == 'active':
        df = calc.activeUsers(service, windowSize=windowSize)
    fig = px.bar(df, x="date", y="counts")
    return fig

app.layout = html.Div([    
    html.Div(children=[
    html.H1(children='LME 검색엔진 사용량(테스트)'),

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
    ),

    html.Div([
    html.Button("Download Excel", id='btn_xlsx'),
    dcc.Download(id='download-datafram-xlsx1')])
    ],

style={'width':'45%', 'float':'left','margin':(10,0,10,0)}),

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

style={'width':'45%', 'float':'right', 'margin':(0,10,10,0)}),

    html.Div(children=[
    html.H1(children='LME 검색엔진 활성 유저수(테스트)'),

    html.Div(children='''
        Window Size (일간/주간/월간)
    '''),
    dcc.Dropdown(
        id='window3',
        options = ['daily','weekly','monthly'],
        value = 'daily'
    ),
    dcc.Graph(
        id='graph3',
        figure = windowedFigure('daily', 'lme_search', type='active')
    )],
    style={'width':'45%', 'float':'bottom', 'margin':(20,20,20,20)})

])

@app.callback(
    Output('download-datafram-xlsx1', 'data'),
    Input('btn_xlsx', 'n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    df = calc.usageCount('lme_search')
    return dcc.send_data_frame(df.to_excel, "lme_search_download_test.xlsx", sheet_name="test")

@app.callback(
    Output("graph1","figure"),
    Input("window1","value")    
)
def updateLME(window):
    figure = windowedFigure(window, 'lme_search')
    return figure

@app.callback(
    Output("graph3","figure"),
    Input("window3","value")    
)
def updateLMEactive(window):
    figure = windowedFigure(window, 'lme_search',type='active')
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