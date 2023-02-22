# visit http://127.0.0.1:3002/ in your web browser.

from dash import Dash, html, dcc #, Input, Output
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform
import plotly.express as px
import pandas as pd
from commons import calc
from datetime import date, datetime, timedelta
from services import lme, kitech, lms

#app = Dash(__name__)
app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])

# see https://plotly.com/python/px-arguments/ for more options

day0 = (datetime.now()-timedelta(days=30)).isoformat()[:10]
day1 = datetime.now().isoformat()[:10]

def datepicker(id0):
    picker = html.Div(['조회 기간 선택',
            html.Div(children=[
                dcc.DatePickerRange(
                id=id0,
                min_date_allowed=date(2018, 1, 1),
                display_format='Y-M-D',
                max_date_allowed=datetime.now(),
                initial_visible_month=date.fromisoformat(day0),
                start_date=day0,
                end_date=day1
                )])],
            style={'position':'relative','width':'70%'}        
        )
    return picker

def windowsize(id0):
    drop = html.Div([
            'Window Size (일간/주간/월간)',
            dcc.Dropdown(
                id=id0,
                options = ['daily','weekly','monthly'],
                value = 'daily')],
            style = {'position':'relative','width':'40%','left':'50%','top':'-67px'}
        )
    return drop

def topNinst(id0):
    drop = html.Div([
        '조회할 기관 수 (상위n개)',
        dcc.Dropdown(
            id=id0,
            options= ['10','15','20','30','max'],
            value = '15'
        )],
        style = {'position':'relative','width':'40%','left':'50%','top':'-67px'}
        )
    return drop

graphSettings = {'lme_usage':{'windowSize':'daily','dateStart':day0,'dateEnd':day1},
                'lme_institute':{'top':'15','dateStart':day0,'dateEnd':day1},
                'lms_usage':{'windowSize':'daily','dateStart':day0,'dateEnd':day1},
                'lms_active':{'windowSize':'daily','dateStart':day0,'dateEnd':day1}}

dfs = {'lme_usage':lme.usage(graphSettings['lme_usage']),
       'lme_institute':lme.institute(graphSettings['lme_institute']),
       'lms_usage':lms.usage(graphSettings['lms_usage']),
       'lms_active':lms.activeUsers(graphSettings['lms_active'])}

app.layout = html.Div([

    ##lme 사용량    
    html.Div(children=[

    html.H1(children='LME 검색엔진 사용량',
        style = {'position':'relative','width':'60%'}),

    ##download button
    html.Div([
            html.Button("Download Excel", id='btn_xlsx1'),
            dcc.Download(id='download-datafram-xlsx1')
            ],
            style = {'position':'relative','width':'20%','left':'300px','top':'-55px','zIndex':5}
    ),

    ##조회기간, window size
    html.Div(children=[
        datepicker('datepicker_lme_usage'),
        windowsize('window1')],
    style = {'position':'relative','zIndex':2}
    ),
        
    html.Div(children=[
        dcc.Graph(
            id='graph1',
            figure = px.bar(dfs['lme_usage'], x="date", y="counts"))],
        style = {'position':'relative','float':'bottom','height':'60%','top':'-60px','zIndex':0}
    )],
    style={'width':'45%', 'float':'left','margin':(10,10,10,10)}
    ),

    #lme 기관별 사용량
    html.Div(children=[
    html.H1(children='LME 검색엔진 기관별 사용량',
        style = {'position':'relative','width':'60%'}),

    ##download button
    html.Div([
            html.Button("Download Excel", id='btn_xlsx2'),
            dcc.Download(id='download-datafram-xlsx2')
            ],
            style = {'position':'relative','width':'20%','left':'400px','top':'-55px'}
    ),

    html.Div(children=[
        datepicker('datepicker_lme_institute'),
        topNinst('topN')],
    style = {'position':'relative','zIndex':2}
    ),  

    html.Div(children=[
        dcc.Graph(
            id='graph3',
            figure = px.bar(dfs['lme_institute'], x="institute", y="counts"))],
        style = {'position':'relative','height':'60%','top':'-60px','zIndex':0}
    )],
    style={'width':'45%', 'float':'right', 'margin':(10,10,10,10)}
    ),

    ##lms 사용량    
    html.Div(children=[

    html.H1(children='LMS 검색엔진 사용량',
        style = {'position':'relative','width':'60%'}),

    ##download button
    html.Div([
            html.Button("Download Excel", id='btn_xlsx3'),
            dcc.Download(id='download-datafram-xlsx3')
            ],
            style = {'position':'relative','width':'20%','left':'300px','top':'-55px'}
    ),

    ##조회기간, window size
    html.Div(children=[
        datepicker('datepicker_lms_usage'),
        windowsize('window_lms_usage')],
    style = {'position':'relative','zIndex':2}
    ),

        
    html.Div(children=[
        dcc.Graph(
            id='graph4',
            figure = px.bar(dfs['lms_usage'], x="date", y="counts"))],
        style = {'position':'relative','float':'bottom','height':'60%','top':'-60px','zIndex':0}
    )],
    style={'width':'45%', 'float':'left', 'margin':(10,10,10,10)}
    ),

    ##lms 사용량    
    html.Div(children=[

    html.H1(children='LMS 활성 유저수',
        style = {'position':'relative','width':'60%'}),

    ##download button
    html.Div([
            html.Button("Download Excel", id='btn_xlsx3'),
            dcc.Download(id='download-datafram-xlsx3')
            ],
            style = {'position':'relative','width':'20%','left':'300px','top':'-55px'}
    ),

    ##조회기간, window size
    html.Div(children=[
        datepicker('datepicker_lms_active'),
        windowsize('window_lms_active')],
    style = {'position':'relative','zIndex':2}
    ),

        
    html.Div(children=[
        dcc.Graph(
            id='graph5',
            figure = px.bar(dfs['lms_active'], x="date", y="counts"))],
        style = {'position':'relative','float':'bottom','height':'60%','top':'-60px','zIndex':0}
    )],
    style={'width':'45%', 'float':'right','margin':(10,10,10,10)}
    )
])

@app.callback(
    Output('download-datafram-xlsx1', 'data'),
    Input('btn_xlsx1', 'n_clicks'),
    prevent_initial_call=True)
def func(n_clicks):
    return dcc.send_data_frame(dfs['lme_usage'].to_excel, "lme_search_usage.xlsx", sheet_name="사용량")

@app.callback(
    Output('download-datafram-xlsx2', 'data'),
    Input('btn_xlsx2', 'n_clicks'),
    prevent_initial_call=True)
def func(n_clicks):
    return dcc.send_data_frame(dfs['lme_institute'].to_excel, "lme_search_institute_usage.xlsx", sheet_name="기관별 사용량")

@app.callback(
    Output('download-datafram-xlsx3', 'data'),
    Input('btn_xlsx3', 'n_clicks'),
    prevent_initial_call=True)
def func(n_clicks):
    return dcc.send_data_frame(dfs['lms_usage'].to_excel, "lms_search_usage.xlsx", sheet_name="사용량")

@app.callback(
    Output('graph1', 'figure'),
    Input('datepicker_lme_usage', 'start_date'),
    Input('datepicker_lme_usage', 'end_date')) 
def updateLMEUsage(start_date, end_date):
    global dfs, graphSettings
    graphSettings['lme_usage']['dateStart'] = start_date
    graphSettings['lme_usage']['dateEnd'] = end_date
    dfs['lme_usage'] = lme.usage(graphSettings['lme_usage'])
    figure = px.bar(dfs['lme_usage'], x="date", y="counts")
    return figure

@app.callback(
    Output("graph1","figure"),
    Input("window1","value"))
def updateLME(window):
    global dfs, graphSettings
    graphSettings['lme_usage']['windowSize'] = window
    dfs['lme_usage'] = lme.usage(graphSettings['lme_usage'])
    figure = px.bar(dfs['lme_usage'], x="date", y="counts")
    return figure

@app.callback(
    Output('graph4', 'figure'),
    Input('datepicker_lms_usage', 'start_date'),
    Input('datepicker_lms_usage', 'end_date')) 
def updateLMSUsage(start_date, end_date):
    global dfs, graphSettings
    graphSettings['lms_usage']['dateStart'] = start_date
    graphSettings['lms_usage']['dateEnd'] = end_date
    dfs['lms_usage'] = lme.usage(graphSettings['lms_usage'])
    figure = px.bar(dfs['lms_usage'], x="date", y="counts")
    return figure

@app.callback(
    Output("graph4","figure"),
    Input('window_lms_usage',"value"))
def updateLMS(window):
    global dfs, graphSettings
    graphSettings['lms_usage']['windowSize'] = window
    dfs['lms_usage'] = lme.usage(graphSettings['lms_usage'])
    figure = px.bar(dfs['lms_usage'], x="date", y="counts")
    return figure

@app.callback(
    Output('graph5', 'figure'),
    Input('datepicker_lms_active', 'start_date'),
    Input('datepicker_lms_active', 'end_date')) 
def updateLMSUsage(start_date, end_date):
    global dfs, graphSettings
    graphSettings['lms_active']['dateStart'] = start_date
    graphSettings['lms_active']['dateEnd'] = end_date
    dfs['lms_active'] = lme.usage(graphSettings['lms_active'])
    figure = px.bar(dfs['lms_active'], x="date", y="counts")
    return figure

@app.callback(
    Output("graph5","figure"),
    Input('window_lms_active',"value"))
def updateLMS(window):
    global dfs, graphSettings
    graphSettings['lms_active']['windowSize'] = window
    dfs['lms_active'] = lme.usage(graphSettings['lms_active'])
    figure = px.bar(dfs['lms_active'], x="date", y="counts")
    return figure

@app.callback(
    Output("graph3", "figure"),
    Input("datepicker_lme_institute", "start_date"),
    Input('datepicker_lme_institute', 'end_date'))    
def updateLMEInstitute(start_date, end_date):
    global dfs, graphSettings
    graphSettings['lme_institute']['dateStart'] = start_date
    graphSettings['lme_institute']['dateEnd'] = end_date
    dfs['lme_institute'] = lme.institute(graphSettings['lme_institute'])
    figure = px.bar(dfs['lme_institute'],x='institute',y='counts')
    return figure
   
@app.callback(
    Output("graph3","figure"),
    Input('topN',"value"))
def updateLMEInstute2(value):
    global dfs, graphSettings
    graphSettings['lme_institute']['top'] = value
    dfs['lme_institute'] = lme.institute(graphSettings['lme_institute'])
    figure = px.bar(dfs['lme_institute'],x='institute',y='counts')
    return figure

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True, port=8090)