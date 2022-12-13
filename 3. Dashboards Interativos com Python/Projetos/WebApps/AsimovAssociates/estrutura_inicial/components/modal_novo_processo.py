from logging import exception
import dash
import plotly.express as px
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from datetime import timedelta, date

import json
import pandas as pd

from app import app

col_centered_style={'display': 'flex', 'justify-content': 'center'}

# ========= Layout ========= #
layout = dbc.Modal([])



# ======= Callbacks ======== #
# Callback para abrir o modal


# Callback para CRUD de processos


# Callback pra atualizar o dropdown de advogados
