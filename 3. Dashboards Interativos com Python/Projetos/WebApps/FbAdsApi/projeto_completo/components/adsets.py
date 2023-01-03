from ctypes import alignment
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from pyrsistent import b
from app import *

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import template_from_url, ThemeChangerAIO

from graph_api import *


# =========  Data Ingestion  =========== #
fb_api = open("tokens/fb_token").read()
ad_acc = "3120164588217844"

fb_api = GraphAPI(ad_acc, fb_api)

campaign_insights = pd.DataFrame(fb_api.get_insights(ad_acc)["data"])
adset_status = pd.DataFrame(fb_api.get_adset_status(ad_acc)["data"])
adset_insights = pd.DataFrame(fb_api.get_insights(ad_acc, "adset")["data"])
ads_insights = pd.DataFrame(fb_api.get_insights(ad_acc, "ad")["data"])


# =========  Layout  =========== #
layout = html.Div([
            dbc.Row([
                html.H3("Selecione o conjunto de anúncio:", style={"margin-top": "50px"}),
                dcc.Dropdown(
                    options=[{"label": i, "value": i} for i in adset_insights.adset_name.values],
                    value=adset_insights.adset_name.values[0],
                    id='dd-adset'),
                ], style={"margin-bottom": "30px"}),

            dbc.Row([
                dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Status"),
                            dbc.CardBody([
                                dbc.Button("", id="btn-adset-status"),
                            ], id="cb-status-adset")
                        ], color="light"),

                    ], md=2),

                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Clicks"),
                            dbc.CardBody([
                                html.H4("", id="adset-clicks", style={"color": "var(--bs-info)"}),
                            ])
                        ], color="light"),

                    ], md=2),

                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Spend"),
                            dbc.CardBody([
                                html.H4("", id="adset-spend", style={"color": "var(--bs-primary)"}),
                            ])
                        ], color="light"),
                    ], md=2),
                
                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Conversion"),
                            dbc.CardBody([
                                html.H5("", id="adset-conversions", style={"color": "var(--bs-primary)"}),
                            ])
                        ], color="light"),
                    ], md=2),
            ]),

            dbc.Row([
                html.H4("Selecione o indicador:"),
                dcc.RadioItems(options=['Spend', 'CPC', 'CPM', 'Clicks', 'Conversion'], 
                            value='Conversion', id='adset-kind', 
                            inputStyle={"margin-right": "5px", "margin-left": "20px"}),
                ], style={"margin-top": "50px"}),

            dbc.Row([            
                dbc.Col(dcc.Graph(id="graph-line-adset"), md=6),
                dbc.Col(dcc.Graph(id="graph-bar-adset"), md=6)
                ], style={"margin-top": "20px"}),
            ]) 

#========== Callbacks ================
@app.callback([
                Output("cb-status-adset", "children"),
                Output("adset-clicks", "children"),
                Output("adset-spend", "children"),
                Output("adset-conversions", "children"),
            ], 
                [Input("dd-adset", "value"),
                ])
def render_page_content(adset):
    adset=adset_insights.adset_name.values[0]

    status = adset_status[adset_status["name"] == adset]["status"].values[0]
    clicks = adset_insights[adset_insights["adset_name"] == adset]["clicks"]
    spend = "R$ " + adset_insights[adset_insights["adset_name"] == adset]["spend"]

    adset_id = adset_status[adset_status["name"] == adset]["id"].values[0]
    data_over_time = fb_api.get_data_over_time(adset_id)
    conversions = pd.DataFrame(data_over_time["data"])["conversion"].fillna(0).sum()

    if status == "PAUSED":
        status = dbc.Button("PAUSED", color="error", size="sm")
    else: 
        status = dbc.Button("ACTIVE", color="primary", size="sm")
    return status, clicks, spend, conversions
    


@app.callback([
                Output("graph-line-adset", "figure"),
                Output("graph-bar-adset", "figure"),
            ], 
                [Input("dd-adset", "value"),
                Input("adset-kind", "value"),
                Input(ThemeChangerAIO.ids.radio("theme"), "value")]
            )
def render_page_content(adset, adset_kind, theme):
    # adset = adset_status["name"].values[0]
    adset_id = adset_status[adset_status["name"] == adset]["id"].values[0]
    # adset_kind = "conversion"
    adset_kind = adset_kind.lower()   
    
    data_over_time = fb_api.get_data_over_time(adset_id)
    df_data = pd.DataFrame(data_over_time["data"])
    df_data["clicks"] = df_data["clicks"].astype(np.float64)
    
    fig_line = px.line(df_data, x="date_start", y=adset_kind, template=template_from_url(theme))
    fig_line.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0))
    
    df_adset = ads_insights[ads_insights["adset_name"]== adset]
    fig_adsets = px.bar(df_adset, y=adset_kind, x="ad_name", template=template_from_url(theme))
    fig_adsets.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0))
    return fig_line, fig_adsets

    