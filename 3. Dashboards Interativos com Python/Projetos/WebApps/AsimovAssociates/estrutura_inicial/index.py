import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3

# import from folders
from app import *
from components import home, sidebar

# Criar estrutura para Store intermediária ==============



# =========  Layout  =========== #
app.layout = dbc.Container([
    # Store e Location 
    

    # Layout
    

], fluid=True)



# ======= Callbacks ======== #
# URL callback to update page content


# Dcc.Store back to file


if __name__ == '__main__':
    app.run_server(debug=True)
