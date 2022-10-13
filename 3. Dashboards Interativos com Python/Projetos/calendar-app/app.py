import dash
import dash_bootstrap_components as dbc


estilos = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"]

app = dash.Dash(__name__, external_stylesheets= estilos + [dbc.themes.DARKLY])
# auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

app.scripts.config.serve_locally = True
server = app.server