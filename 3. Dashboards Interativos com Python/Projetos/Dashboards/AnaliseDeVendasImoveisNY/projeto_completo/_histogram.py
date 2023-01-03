from textwrap import dedent
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import json
import dash
from app import app
# from globals import *
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt



fig = go.Figure()
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0, 0, 0, 0)")
# go.Figure().layout = hist_layout

hist = dbc.Row([
                dcc.Graph(id="hist-graph", figure=fig)
                ], style={"height": "20vh"})









