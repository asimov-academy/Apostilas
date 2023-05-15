import dash
import dash_bootstrap_components as dbc

estilos = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css", "https://fonts.googleapis.com/icon?family=Material+Icons"]

app = dash.Dash(external_stylesheets= estilos + [dbc.themes.BOOTSTRAP])

app.config['suppress_callback_exceptions'] = True
app.scripts.config.serve_locally = True
server = app.server
