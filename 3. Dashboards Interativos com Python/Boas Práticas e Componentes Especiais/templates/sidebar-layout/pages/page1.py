from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import *

import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# =========  Layout  =========== #
layout = html.Div([
            html.H3("Page1")
        ]) 



# =========  Callbacks Page1  =========== #
# ..