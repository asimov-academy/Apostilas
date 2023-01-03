from textwrap import dedent
import dash_player
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_extensions import Keyboard
import json
import dash
from app import app
from globals import *


r_controls = dbc.Col([
                    dcc.Dropdown(id="dd-my-videos-r",
                            options=[{"label": i, "value": j} for i, j in MY_VIDEOS.items()],
                            value=list(MY_VIDEOS.values())[-1],
                            style={"margin-top": "10px"},
                            placeholder="Selecione seu vídeo"),

                    dbc.Card([   
                        dbc.CardBody([
                            dbc.Input(id="inpt-cut-name-r", placeholder="Nome do corte", type="text"),
                            dcc.RadioItems(
                                id='rd-cut-kind-r',
                                options=[{'label': 'Forehand', 'value': 'forehand'},
                                    {'label': 'Backhand', 'value': 'backhand'},
                                    {'label': 'Saque', 'value': 'saque'},
                                    {'label': 'Ponto', 'value': 'ponto'},
                                    {'label': 'Outro', 'value': 'outro'}],
                                value='forehand', labelStyle={'display': 'inline-block', 'margin': '10px'}),

                            dbc.Row([
                                dbc.Button("Início: 0", color="secondary", id="btn-set-start-r", size="lg"),
                                dbc.Button("Fim: 10", color="secondary", id="btn-set-end-r", size="lg"),
                                dbc.Button("Criar corte", color="info", id="btn-create-cut-r", size="lg")]),
                        ])], color="dark", outline=True),

                    dbc.Row([
                        dbc.Col([dbc.Button("Deletar", color="danger", id="btn-delete-cut-r", size="lg")], md="1", style={"margin-top": "10px"}),
                        dbc.Col([dcc.Dropdown(id="dd-cut-scenes-r", style={"margin-top": "10px"}, placeholder="Selecione seu corte")], md="11")
                        ]),
                   
                    dash_player.DashPlayer(id='video-player-r',
                        controls=True,
                        width='100%', 
                        height="600px",
                        intervalSecondsLoaded=200,
                        style={"margin-top": "10px"}),

                    ])

                
@app.callback(Output('video-player-r', 'url'),
              [Input('dd-my-videos-r', 'value')])
def select_video_1(value):
    return value


@app.callback(Output('btn-set-start-r', 'children'),
              [Input('btn-set-start-r', 'n_clicks'), State('video-player-r', 'currentTime')])
def update_btn_start1(n_clicks, value):
    value = 0 if value is None else value
    return "INÍCIO: {:.1f}".format(value)


@app.callback(Output('btn-set-end-r', 'children'),
              [Input('btn-set-end-r', 'n_clicks'), State('video-player-r', 'currentTime')])
def update_btn_end1(n_clicks, value):
    value = 10 if value is None else value
    return "FIM: {:.1f}".format(value)


@app.callback(Output('dd-cut-scenes-r', 'options'),
              [Input('btn-create-cut-r', 'n_clicks'), Input('btn-delete-cut-r', 'n_clicks'),
              State('btn-set-start-r', 'children'), 
              State('btn-set-end-r', 'children'), State('video-player-r', 'duration'),
              State('inpt-cut-name-r', 'value'), Input('video-player-r', 'url'), 
              State('rd-cut-kind-r', 'value'), State('dd-cut-scenes-r', 'value')])
def create_cut_1(create_cut, delete_cut, start, end, duration, 
                cut_name, url, cut_kind, selected_scene):
    global DICT_SCENES
    if "btn-create-cut-r.n_clicks" == dash.callback_context.triggered[0]["prop_id"]:
        start = float(start.split(":")[1])
        end = float(end.split(":")[1])
        DICT_SCENES[url][cut_kind.upper() + " : " + cut_name] = [start, end]
    
    elif "btn-delete-cut-r.n_clicks" == dash.callback_context.triggered[0]["prop_id"]:
        if selected_scene is not None:
            del DICT_SCENES[url][selected_scene]

    with open('dict_scenes.json', 'w') as f:
            json.dump(DICT_SCENES, f)
    return [{"label": i, "value": i} for i in DICT_SCENES[url].keys()]


@app.callback(Output('video-player-r', 'seekTo'),
              [Input('dd-cut-scenes-r', 'value'), 
              State('video-player-r', 'url'), Input('video-player-r', 'currentTime')])
def control_scene_time1(cut_scene, url, current_time):
    global DICT_SCENES

    if cut_scene is not None:
        if current_time < DICT_SCENES[url][cut_scene][0]:
            return DICT_SCENES[url][cut_scene][0]
        elif current_time > DICT_SCENES[url][cut_scene][1]:
            return DICT_SCENES[url][cut_scene][0]