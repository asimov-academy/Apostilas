from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from pyrsistent import b
from app import *

from graph_api import *

# FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
# dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY, FONT_AWESOME, dbc_css],
#         suppress_callback_exceptions=True)



# =========  Data Ingestion  =========== #
fb_api = open("tokens/fb_token").read()
ad_acc = "3120164588217844"

fb_api = GraphAPI(ad_acc, fb_api)

campaign_insights = pd.DataFrame(fb_api.get_campaign_insights(ad_acc)["data"])
campaign_status = pd.DataFrame(fb_api.get_campaigns_status(ad_acc)["data"])
data_over_time = fb_api.get_data_over_time(23850222223840625)


card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

# =========  Layout  =========== #
layout = dbc.Container([
            dbc.Row([
                html.H3("Selecione a campanha:", style={"margin-top": "50px"}),
                dcc.Dropdown(
                    options=[{"label": i, "value": i} for i in campaign_insights.campaign_name.values],
                    id='dd-campaign', style={"margin-bottom": "20px"}),
                # html.Hr(),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.CardGroup([
                            dbc.Card([
                                    html.H5("Status"),
                                    html.P("", id="p-campaign-status", className="card-text"),
                            ]),
                            dbc.Card(
                                html.Div(className="fa fa-list", style=card_icon), 
                                color="primary",
                                style={"maxWidth": 75, "height": 100},
                            )])
                    ]),

                dbc.Col([
                    dbc.CardGroup([
                            dbc.Card([
                                    html.H5("Card 1"),
                                    html.P("This card has some text content", className="card-text")]
                            ),
                            dbc.Card(
                                html.Div(className="fa fa-list", style=card_icon), 
                                color="info",
                                style={"maxWidth": 75})
                            ])
                    ]),

                dbc.Col([
                    dbc.CardGroup([
                            dbc.Card([
                                    html.H5("Card 1"),
                                    html.P("This card has some text content")
                                ]),
                            dbc.Card(
                                html.Div(className="fa fa-list", style=card_icon), 
                                color="secondary",
                                style={"maxWidth": 75},
                            )])
                    ]),
            ]),

            dbc.Row([
                dbc.Col([
                        dcc.Graph(id="graph-line-campaign")
                ], md=9),

                dbc.Col([
                    dcc.Graph(id="graph-bar-campaign")
                ], md=3)
            ])
        ]) 

# ========== Components ================
@app.callback(Output("p-campaign-status", "children"), 
                [Input("dd-campaign", "value")])
def render_page_content(value):
    return campaign_status[campaign_status["name"] == value]["status"]