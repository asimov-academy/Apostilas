import dash
import dash_bootstrap_components as dbc
import dash_auth


dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ, dbc_css],
        suppress_callback_exceptions=True)

app.scripts.config.serve_locally = True
server = app.server
 