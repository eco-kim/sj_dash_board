# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from modules import calc
from datetime import date, datetime, timedelta

app = Dash(__name__)

# see https://plotly.com/python/px-arguments/ for more options

def windowedFigure(windowSize, service, type='usage'):
    if type == 'usage':
        df = calc.usageCount(service, windowSize=windowSize)
    elif type == 'active':
        df = calc.activeUsers(service, windowSize=windowSize)
    fig = px.bar(df, x="date", y="counts")
    return fig

def instituteFigure(start_date, end_date):
    df = calc.institute(start_date, end_date)
    df = df.iloc[:15]
    fig = px.bar(df, x="institute", y="counts")
    return fig

day0 = (datetime.now()-timedelta(days=7)).isoformat()[:10]
day1 = datetime.now().isoformat()[:10]
instituteDF = calc.institute(day0,day1)

app.layout = html.Div([    
    html.Div(children=[
    html.H1(children='LME 검색엔진 사용량'),

    html.Div(children=[
        html.Div([
            'Window Size (일간/주간/월간)',
            dcc.Dropdown(
                id='window1',
                options = ['daily','weekly','monthly'],
                value = 'daily')],
            style = {'position':'relative','width':'40%'}
        ),
        html.Div([
            html.Button("Download Excel", id='btn_xlsx1'),
            dcc.Download(id='download-datafram-xlsx1')
            ],
            style = {'position':'relative','left':'370px','top':'-30px'}
        ),
        html.Div(
            dcc.Graph(
                id='graph1',
                figure = windowedFigure('daily', 'lme_search')),
            style = {'position':'relative','top':'-20px'}
        )        
    ])],
    style={'width':'45%', 'float':'left','margin':(10,0,10,0)}
    ),

    html.Div(children=[
    html.H1(children='LME 검색엔진 기관별 사용량'),

    html.Div(children=[
        html.Div(['조회 기간 선택',
            html.Div([
                dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(2018, 1, 1),
                display_format='Y-M-D',
                max_date_allowed=datetime.now(),
                initial_visible_month=datetime.now(),
                start_date=day0,
                end_date=day1,
                style={'height':'1px','font-size':'50%','z-index':99}
                )],
        
            )]
        ),
        html.Div([
            html.Button("Download Excel", id='btn_xlsx2'),
            dcc.Download(id='download-datafram-xlsx2')
            ],
            style = {'position':'relative','left':'370px','top':'-30px'}
        ),
        html.Div(
        dcc.Graph(
            id='graph3',
            figure = instituteFigure((datetime.now()-timedelta(days=7)).isoformat()[:10], datetime.now().isoformat()[:10])),
        style = {'position':'relative','top':'-20px','z-index':0}
        )
    ])],
    style={'width':'45%', 'float':'right', 'margin':(0,10,10,0)}
    ),


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
   
    style={'width':'45%', 'float':'bottom', 'margin':(20,20,20,20)})

])

@app.callback(
    Output('download-datafram-xlsx1', 'data'),
    Input('btn_xlsx1', 'n_clicks'),
    prevent_initial_call=True)
def func(n_clicks):
    df = calc.usageCount('lme_search')
    return dcc.send_data_frame(df.to_excel, "lme_search_usage.xlsx", sheet_name="사용량")

@app.callback(
    Output('download-datafram-xlsx2', 'data'),
    Input('btn_xlsx2', 'n_clicks'),
    prevent_initial_call=True
)
def func(n_clicks):
    return dcc.send_data_frame(instituteDF.to_excel, "lme_search_institute_usage.xlsx", sheet_name="기관별 사용량")

@app.callback(
    Output("graph1","figure"),
    Input("window1","value")    
)
def updateLME(window):
    figure = windowedFigure(window, 'lme_search')
    return figure

@app.callback(
    Output("graph2","figure"),
    Input("window2","value"))
def updateKITECH(window):
    figure = windowedFigure(window, 'kitech_api')
    return figure

@app.callback(
    Output('graph3', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))    
def updateLMEInstitute(start_date, end_date):
    global instituteDF
    figure = instituteFigure(start_date, end_date)
    instituteDF = calc.institute(start_date, end_date)
    return figure
   

if __name__ == '__main__':
    app.run_server(debug=True, port=3002)