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
adset_insights = pd.DataFrame(fb_api.get_insights(ad_acc, "adset")["data"])
campaign_status = pd.DataFrame(fb_api.get_campaigns_status(ad_acc)["data"])


adset_insights.head(3)
# data_over_time = fb_api.get_data_over_time(23849930731190625)
data_over_time = fb_api.get_data_over_time(23849930731250625)["data"]


# =========  Layout  =========== #
layout = html.Div([
            dbc.Row([
                html.H3("Selecione a campanha:", style={"margin-top": "50px"}),
                dcc.Dropdown(
                    options=[{"label": i, "value": i} for i in campaign_insights.campaign_name.values],
                    value=campaign_insights.campaign_name.values[0],
                    id='dd-campaign'),
                ], style={"margin-bottom": "30px"}),

            dbc.Row([
                dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Status"),
                            dbc.CardBody([
                            ], id="cb-status")
                        ], color="light"),

                    ], md=2),

                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Clicks"),
                            dbc.CardBody([
                                html.H4("", id="campaign-clicks", style={"color": "var(--bs-info)"}),
                            ])
                        ], color="light"),

                    ], md=2),

                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Spend"),
                            dbc.CardBody([
                                html.H4("", id="campaign-spend", style={"color": "var(--bs-primary)"}),
                            ])
                        ], color="light"),
                    ], md=2),
                
                dbc.Col([
                    dbc.Card([
                            dbc.CardHeader("Conversion"),
                            dbc.CardBody([
                                html.H5("", id="campaign-conversions", style={"color": "var(--bs-primary)"}),
                            ])
                        ], color="light"),
                    ], md=2),
            ]),

            dbc.Row([
                html.H4("Selecione o indicador:"),
                dcc.RadioItems(options=['Spend', 'CPC', 'CPM', 'Clicks', 'Conversion'], 
                            value='Conversion', id='campaign-kind', 
                            inputStyle={"margin-right": "5px", "margin-left": "20px"}),
                ], style={"margin-top": "50px"}),

            dbc.Row([            
                dbc.Col(dcc.Graph(id="graph-line-campaign"), md=6),
                dbc.Col(dcc.Graph(id="graph-bar-campaign"), md=6)
                ], style={"margin-top": "20px"}),
            ]) 

#========== Callbacks ================
@app.callback([
                Output("cb-status", "children"),
                Output("campaign-clicks", "children"),
                Output("campaign-spend", "children"),
                Output("campaign-conversions", "children"),
            ], 
                [Input("dd-campaign", "value"),
                ])
def render_page_content(campaign):
    status = campaign_status[campaign_status["name"] == campaign]["status"].values[0]
    clicks = campaign_insights[campaign_insights["campaign_name"] == campaign]["clicks"]
    spend = "R$ " + campaign_insights[campaign_insights["campaign_name"] == campaign]["spend"]

    campaign_id = campaign_status[campaign_status["name"] == campaign]["id"].values[0]
    data_over_time = fb_api.get_data_over_time(campaign_id)
    conversions = pd.DataFrame(data_over_time["data"])["conversion"].fillna(0).sum()

    if status == "PAUSED":
        status = dbc.Button("PAUSED", color="error", size="sm")
    else: 
        status = dbc.Button("ACTIVE", color="primary", size="sm")
    return status, clicks, spend, conversions
    

@app.callback([
                Output("graph-line-campaign", "figure"),
                Output("graph-bar-campaign", "figure"),
            ], 
                [Input("dd-campaign", "value"),
                Input("campaign-kind", "value"),
                Input(ThemeChangerAIO.ids.radio("theme"), "value")]
            )
def render_page_content(campaign, campaign_kind, theme):
    campaign_kind = campaign_kind.lower()

    campaign_id = campaign_status[campaign_status["name"] == campaign]["id"].values[0]
    data_over_time = fb_api.get_data_over_time(campaign_id)
    df_data = pd.DataFrame(data_over_time["data"])
    df_data["clicks"] = df_data["clicks"].astype(np.float64)
    
    fig_line = px.line(df_data, x="date_start", y=campaign_kind, template=template_from_url(theme))
    fig_line.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0))

    df_adset = adset_insights[adset_insights["campaign_name"]== campaign]
    fig_adsets = px.bar(df_adset, y=campaign_kind, x="adset_id", template=template_from_url(theme))
    fig_adsets.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0))
    return fig_line, fig_adsets

    