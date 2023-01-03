import dash
import dash_bootstrap_components as dbc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server
app.scripts.config.serve_locally = True
server = app.server
 