#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash
import plotly.io as pio
import plotly.express as px
import sys
#get_ipython().system('{sys.executable} -m pip install plotly pandas numpy==1.19.3 ipython==7.16.1 psutil dash_bootstrap_components gunicorn')


# In[2]:


import pandas as pd
pd.set_option('max_rows', 20)
pio.renderers.default = "browser"


# In[3]:


# In[4]:


CONF_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
DEAD_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
RECV_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'


# In[5]:


covid_conf_ts = pd.read_csv(CONF_URL)
covid_dead_ts = pd.read_csv(DEAD_URL)
covid_recv_ts = pd.read_csv(RECV_URL)


# In[6]:


# get data in cleaned time series format for country
def process_data(data, cntry='Canada', window=3):
    conf_ts = data
    conf_ts_cntry = conf_ts[conf_ts['Country/Region'] == cntry]
    final_dataset = conf_ts_cntry.T[4:].sum(
        axis='columns').diff().rolling(window=window).mean()[40:]
    df = pd.DataFrame(final_dataset, columns=['Total'])
    return df


# In[7]:


def get_overall_total(df):
    return df.iloc[:, -1].sum()


conf_overall_total = get_overall_total(covid_conf_ts)
dead_overall_total = get_overall_total(covid_dead_ts)
recv_overall_total = get_overall_total(covid_recv_ts)
active_cntry_total = conf_overall_total - \
    recv_overall_total - dead_overall_total
print('Overall Confirmed:', conf_overall_total)
print('Overall Dead:', dead_overall_total)
print('Overall Recovered:', recv_overall_total)
print('Overall Active:', active_cntry_total)


# In[8]:


def get_cntry_total(df, cntry='Canada'):
    return df[df['Country/Region'] == cntry].iloc[:, -1].sum()


cntry = 'Canada'
conf_cntry_total = get_cntry_total(covid_conf_ts, cntry)
dead_cntry_total = get_cntry_total(covid_dead_ts, cntry)
recv_cntry_total = get_cntry_total(covid_recv_ts, cntry)
active_cntry_total = conf_cntry_total - recv_cntry_total - dead_cntry_total
print(f'{cntry} Confirmed:', conf_cntry_total)
print(f'{cntry} Dead:', dead_cntry_total)
print(f'{cntry} Recovered:', recv_cntry_total)
print(f'{cntry} Recovered:', active_cntry_total)


# In[9]:


def doughnut_fig(cntry='Canada', window=3):
    conf_cntry_total = get_cntry_total(covid_conf_ts, cntry)
    dead_cntry_total = get_cntry_total(covid_dead_ts, cntry)
    recv_cntry_total = get_cntry_total(covid_recv_ts, cntry)
    active_cntry_total = conf_cntry_total - recv_cntry_total - dead_cntry_total

    df = pd.DataFrame(data=[active_cntry_total, dead_cntry_total, recv_cntry_total],
                      index=['Active', 'Dead', 'Recovered'],
                      columns=['Total'])

    fig = px.pie(df, values='Total',
                 names=df.index,
                 labels=['Confirmed', 'Dead', 'Recovered'],
                 hole=.6,
                 title='Overall Situation at ' + format(
                     cntry)+' : '+format(conf_cntry_total),
                 color=df.index, color_discrete_map={'Active': 'indianred',
                                                     'Recovered': 'mediumseagreen',
                                                     'Dead': 'black'})

    fig.update_traces(textposition='outside', textinfo='percent',
                      textfont_size=20, showlegend=True,
                      insidetextorientation='horizontal')

    fig.update_layout(title_x=0.5,
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=-0.3,
                          xanchor="center",
                          x=0.5
                      ))
    return fig


# In[10]:


def fig_world_trend(cntry='Canada', window=3):
    df = process_data(data=covid_conf_ts, cntry=cntry, window=window)
    df.head(10)
    if window == 1:
        yaxis_title = "Daily Cases"
    else:
        yaxis_title = "Daily Cases ({}-day MA)".format(window)
    fig = px.line(df, y='Total', x=df.index, title='Daily confirmed cases trend for {}'.format(
        cntry), color_discrete_sequence=['#FFC34D'])
    fig.update_layout(title_x=0.5, xaxis_title=" ",
                      plot_bgcolor='#ffffff', yaxis_title=yaxis_title)
    return fig


# In[11]:


external_stylesheets = [dbc.themes.BOOTSTRAP]


# In[12]:


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Covid-19 Tracker'
server = app.server


# In[13]:


def get_country_list():
    return covid_conf_ts['Country/Region'].unique()


def create_dropdown_list(cntry_list):
    dropdown_list = []
    for cntry in sorted(cntry_list):
        tmp_dict = {'label': cntry, 'value': cntry}
        dropdown_list.append(tmp_dict)
    return dropdown_list


def get_country_dropdown(id):

    return dbc.Form(
        [
            dbc.FormGroup(
                [
                    dbc.Label("Select a country", className="mr-2",
                              style={'color': '#ffffff'}),
                    dcc.Dropdown(id='my-id'+str(id),
                                 options=create_dropdown_list(
                                     get_country_list()),
                                 value='Canada',
                                 clearable=False,
                                 style={'width': '170px'}
                                 ),
                ],
                className="mr-3",
            ),
            html.Div(id='my-div'+str(id))
        ],
        inline=True
    )


# In[14]:


def graph1():
    return dcc.Graph(id='graph1', figure=fig_world_trend('Canada'), style={'height': '70vh'})


# In[15]:


def graph2():
    return dcc.Graph(id='graph2', figure=doughnut_fig('Canada'), style={'height': '70vh'})


# In[16]:


def get_slider():
    return html.Div([
        dcc.Slider(
            id='my-slider',
            min=1,
            max=15,
            step=None,
            marks={
                1: '1',
                3: '3',
                5: '5',
                7: '1-Week',
                14: 'Fortnight'
            },
            value=3,
        ),
        html.Div([html.Label('Select Moving Average Window')],
                 id='my-div'+str(id), style={'textAlign': 'center'})
    ])


# In[17]:


def generate_layout():
    layout = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(html.H3("Covid Tracker"), width=4,
                            style={'color': '#ffffff', "height": "100%"}),
                    dbc.Col(get_country_dropdown(
                        id=1), width={'size': 4}, style={'height': '100%'})

                ],
                justify="between",
                style={'border': '2px solid black',
                       'background-color': '#2a3f54'},
                # className="h-20",

            ),
            dbc.Row(
                [
                    dbc.Col(html.Div('Worldwide Confirmed Cases: ' + str(conf_overall_total)), lg=3, sm=6,
                            style={"height": "100%", 'border-right': '1px solid', 'border-bottom': '1px solid', 'background': '#FFC34D'}),
                    dbc.Col(html.Div(
                        'Worldwide Active Cases: ' + str(active_cntry_total)), lg=3, sm=6,
                        style={"height": "100%", 'border-right': '1px solid', 'border-bottom': '1px solid', 'background': '#C46060'
                               }),
                    dbc.Col(html.Div('Worldwide Recovered Cases: ' + str(recv_overall_total)), lg=3, sm=6,
                            style={"height": "100%", 'border-right': '1px solid', 'border-bottom': '1px solid', 'background': '#8CC466'}),
                    dbc.Col(html.Div('Worldwide Death Cases: ' + str(dead_overall_total)), lg=3, sm=6,
                            style={"height": "100%", 'border-bottom': '1px solid', 'background': '#A9ADC4'}),
                ],
                style={'margin-left': 0, 'text-align': 'center'},
                # className="h-30",
            ),
            dbc.Row(
                [

                    dbc.Col(graph2(), lg=6, sm=12, style={
                            'border-right': '1px solid black'}),
                    dbc.Col([graph1(),
                             dbc.Col(get_slider())
                             ], lg=6, sm=12),
                ],
                # justify="between",
                style={'margin-left': 0},
                # className="h-30",
            ),
            dbc.Row([
                dbc.Col(
                    html.P("Visualization by Plotly"),
                    style={'margin-left': 0, 'background': '#DCDCDC',
                           'text-align': 'end', 'padding-right': '35px', 'padding-top': '15px'}
                )],
                style={'margin-left': 0},
                # className="h-20"
            ),

        ], fluid=True, style={'padding': '0', 'margin': '0', 'overflow': 'hidden'}
    )
    return layout


# In[18]:


app.layout = generate_layout()


# In[19]:


@app.callback(
    [Output(component_id='graph1', component_property='figure'),  # line chart
     Output(component_id='graph2', component_property='figure')],  # doughnut chart
    [Input(component_id='my-id1', component_property='value'),  # dropdown
     Input(component_id='my-slider', component_property='value')]  # slider
)
def update_output_div(input_value1, input_value2):
    return fig_world_trend(input_value1, input_value2), doughnut_fig(input_value1)
#     return fig_world_trend(input_value1,input_value2)


# In[ ]:

if __name__ == "__main__":
    app.run_server(host='127.0.0.1', debug=False)


# In[ ]:
