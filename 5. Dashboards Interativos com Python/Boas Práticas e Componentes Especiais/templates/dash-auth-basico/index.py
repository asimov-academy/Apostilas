from dash import html, dcc
import dash_bootstrap_components as dbc
import dash

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# pip install dash-auth
import dash_auth


from dash_bootstrap_templates import load_figure_template
load_figure_template(["quartz"])

VALID_USERNAME_PASSWORD_PAIRS = {
    'rodrigo': '1234'
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
server = app.server


card_style = {
    'width': '800px',
    'min-height': '300px',
    'padding': '25px',
    'align-self': 'center'
}
df = pd.DataFrame(np.random.randn(100, 1), columns=["data"])
fig = px.line(df, x=df.index, y="data", template="quartz")

# =========  Layout  =========== #
app.layout =  html.Div([
                dbc.Card([
                    dcc.Graph(figure=fig),

                ], style=card_style)
            ], style={"height": "100vh", "vertical-align": "middle", "display": "flex", "justify-content": "center"})


if __name__ == "__main__":
    app.run_server(port=8051, debug=True)