from dash import html, dcc
import dash_bootstrap_components as dbc
from app import app
import plotly.graph_objects as go



fig = go.Figure()
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0, 0, 0, 0)")


map = dbc.Row([
                dcc.Graph(id="map-graph", figure=fig)
            ], style={"height": "80vh"})







