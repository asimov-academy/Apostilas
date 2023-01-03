from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from left_video import *
from notes_form import *
# import callbacks

app.layout = dbc.Container(
        children=[
            dbc.Row([
                dbc.Col([
                    html.Img(id="logo", src=app.get_asset_url("logo_dark.png"), height=50, 
                    style={"margin-bottom": "20px"}),

                    dcc.Slider(id='slider-playback-rate', min=0.25, max=5, 
                    step=None, marks={i: str(i) + 'x' for i in [0.25, 1, 2, 5]}, value=1),
                    
                    l_controls
                ], md="9"),

                dbc.Col([
                    notes_form
                ], md="3")

            ]),
        ], fluid=True, style={"padding": "50px 50px"})


@app.callback(Output('video-player', 'playbackRate'),
              [Input('slider-playback-rate', 'value')])
def update_playbackRate(value):
    return value


if __name__ == '__main__':
    app.run_server(debug=False)