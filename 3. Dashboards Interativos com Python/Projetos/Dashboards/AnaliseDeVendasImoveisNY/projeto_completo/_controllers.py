

from dash import html, dcc
import dash_bootstrap_components as dbc
from app import app


list_of_locations = {
    "All": 0,
    "Manhattan": 1,
    "Bronx": 2,
    "Brooklyn": 3,
    "Queens": 4,
    "Staten Island ": 5,
}

slider_size = [100, 500, 1000, 10000, 10000000]

controllers = dbc.Row([
                dcc.Store(id='store-global'),
                html.Img(id="logo", src=app.get_asset_url("logo_dark.png"), style={'width':'50%'}),
                html.H3("Vendas de imóveis - NYC", style={"margin-top": "30px"}),
                html.P(
                """Utilize este dashboard para analisar vendas ocorridas na 
                cidade de New York no período de 1 ano. """
                ),

                html.H4("""Borough""", style={"margin-top": "50px", "margin-bottom": "50px"}),
                dcc.Dropdown(
                    id="location-dropdown",
                    options=[{"label": i, "value": j} for i, j in list_of_locations.items()],
                    value=0,
                    placeholder="Select a borought"),

                html.P("""Metragem (m2)""", style={"margin-top": "20px"}),

                dcc.Slider(min=0, max=4, id='slider-square-size', value=4,
                marks = {i: str(j)for i, j in enumerate(slider_size)}),

                html.P("""Variável de análise""", style={"margin-top": "20px"}),
                
                dcc.Dropdown(
                    options=[
                        {'label': 'YEAR BUILT', 'value': 'YEAR BUILT'},
                        {'label': 'TOTAL UNITS', 'value': 'TOTAL UNITS'},
                        {'label': 'SALE PRICE', 'value': 'SALE PRICE'},
                    ],
                    value='SALE PRICE',
                    id="dropdown-color")
    ])

    





