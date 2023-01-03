from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
from app import app


style_sidebar = style={"box-shadow": "2px 2px 10px 0px rgba(10, 9, 7, 0.10)",
                    "margin": "10px",
                    "padding": "10px",
                    "height": "100vh"}

# =========  Layout  =========== #
layout = dbc.Card(
    [
        html.H2("ASIMOV", style={'font-family': 'Voltaire', 'font-size': '60px'}),
        html.Hr(), 
        html.P("A simple sidebar layout with navigation links", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Campaigns", href="/", active="exact"),
                dbc.NavLink("Adsets", href="/adsets", active="exact"),
            ], vertical=True, pills=True, style={"margin-bottom": "50px"}),
        ThemeChangerAIO(aio_id="theme", radio_props={"value":dbc.themes.QUARTZ})
    ], style=style_sidebar
)

