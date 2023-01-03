import dash_player
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import json
import dash
from app import app
from globals import *


l_controls = dbc.Col([
                    dcc.Dropdown(id="dd-my-videos",
                            options=[{"label": i, "value": j} for i, j in MY_VIDEOS.items()],
                            value=list(MY_VIDEOS.values())[-1],
                            style={"margin-top": "10px"},
                            placeholder="Selecione seu vídeo"),

                    dbc.Collapse(
                        dbc.Card([   
                            dbc.CardBody([
                                dbc.Input(id="inpt-cut-name", placeholder="Nome do corte", 
                                type="text"),
                                dcc.RadioItems(
                                    id='rd-cut-kind',
                                    options=[{'label': 'Forehand', 'value': 'forehand'},
                                        {'label': 'Backhand', 'value': 'backhand'},
                                        {'label': 'Saque', 'value': 'saque'},
                                        {'label': 'Ponto', 'value': 'ponto'},
                                        {'label': 'Outro', 'value': 'outro'}],
                                    value='forehand', labelStyle={'display': 'inline-block', 
                                    'margin': '10px'}),
                                
                                dbc.Row([
                                    dbc.Button("Início: 0", color="secondary", 
                                    id="btn-set-start", size="lg", style={"width": "150px"}),

                                    dbc.Button("Fim: 10", color="secondary", 
                                    id="btn-set-end", size="lg", style={"width": "150px"}),

                                    dbc.Button("Criar corte", color="info", 
                                    id="btn-create-cut", size="lg", style={"width": "150px"})]),

                            ])], color="dark", outline=True), 
                        id="collapse", is_open=False, style={"margin-top": "25px", 
                        "margin-bottom": "25px"}),

                    dbc.Row([
                        dbc.Col(dbc.Button("Cortes", color="info", id="btn-collapse", 
                        size="lg"), md="1", style={"margin-top": "10px"}),

                        dbc.Col(dbc.Button("Deletar", color="danger", id="btn-delete-cut", 
                        size="lg"), md="1", style={"margin-top": "10px"}),

                        dbc.Col(dcc.Dropdown(id="dd-cut-scenes", style={"margin-top": "10px"}, 
                        placeholder="Selecione seu corte"), md="10")
                    ]),
                   
                    dash_player.DashPlayer(id='video-player',
                        controls=True,
                        width='100%', 
                        height="600px",
                        intervalSecondsLoaded=200,
                        style={"margin-top": "20px"}),

                    ])

@app.callback(
    Output("collapse", "is_open"),
    [Input("btn-collapse", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(Output('video-player', 'url'),
              [Input('dd-my-videos', 'value')])
def select_video_1(value):
    return value


@app.callback(Output('btn-set-start', 'children'),
              [Input('btn-set-start', 'n_clicks'), State('video-player', 'currentTime')])
def update_btn_start1(n_clicks, value):
    value = 0 if value is None else value
    return "INÍCIO: {:.1f}".format(value)


@app.callback(Output('btn-set-end', 'children'),
              [Input('btn-set-end', 'n_clicks'), State('video-player', 'currentTime')])
def update_btn_end1(n_clicks, value):
    value = 10 if value is None else value
    return "FIM: {:.1f}".format(value)


@app.callback(Output('dd-cut-scenes', 'options'),

              [Input('btn-create-cut', 'n_clicks'), Input('btn-delete-cut', 'n_clicks'),
              Input('video-player', 'url')],

              [State('btn-set-start', 'children'), 
              State('btn-set-end', 'children'), State('inpt-cut-name', 'value'),  
              State('rd-cut-kind', 'value'), State('dd-cut-scenes', 'value')])
def create_cut_1(create_cut, delete_cut, url, start, end,
                cut_name, cut_kind, selected_scene):
    if "btn-create-cut.n_clicks" == dash.callback_context.triggered[0]["prop_id"]:
        start = float(start.split(":")[1])
        end = float(end.split(":")[1])
        DICT_SCENES[url][cut_kind.upper() + " : " + cut_name] = [start, end]
    
    elif "btn-delete-cut.n_clicks" == dash.callback_context.triggered[0]["prop_id"]:
        if selected_scene is not None:
            del DICT_SCENES[url][selected_scene]

    with open('dict_scenes.json', 'w') as f:
            json.dump(DICT_SCENES, f)
    return [{"label": i, "value": i} for i in DICT_SCENES[url].keys()]


@app.callback(Output('video-player', 'seekTo'),
              [Input('dd-cut-scenes', 'value'), 
              State('video-player', 'url'), Input('video-player', 'currentTime')])
def control_scene_time1(cut_scene, url, current_time):
    if cut_scene is not None:
        if current_time < DICT_SCENES[url][cut_scene][0]:
            return DICT_SCENES[url][cut_scene][0]
        elif current_time > DICT_SCENES[url][cut_scene][1]:
            return DICT_SCENES[url][cut_scene][0]