import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from app import app
from copy import deepcopy
from globals import *
import json


notes_form = html.Div([
                    html.H6("Anotações", className="display-4", 
                    style={"margin-left": "10px"}),

                    dbc.Button("Salvar nota", color="info", size="lg", 
                    id="btn-save-note", style={"margin-top": "10px", "margin-bottom": "10px"}),

                    dbc.Textarea(size="lg", id="txt-notes", 
                                placeholder="Notas do vídeo ou corte", 
                                style={'width': '100%', 'height': "90%", 
                                "margin-left": "10px"}),

        ], className="h-100 p-5 text-white rounded-3")


@app.callback(Output("txt-notes", "value"),
              [Input('btn-save-note', 'n_clicks'), State("txt-notes", "value"),
              Input("video-player", "url"), Input("dd-cut-scenes", "value")])
def update_notes(n_clicks, note, url, cut_scene):
    cut_scene = "" if cut_scene is None else cut_scene
    url = "" if url is None else url
    key_name = url + "-" + cut_scene

    trigg = dash.callback_context.triggered[0]["prop_id"]
    if "btn-save-note.n_clicks" == trigg:
        DICT_NOTES[key_name] = note
        with open('dict_notes.json', 'w') as f:
            json.dump(DICT_NOTES, f)
        return DICT_NOTES[key_name]
        
    if ("video-player.url" in trigg or "dd-cut-scenes.value" in trigg) and key_name in DICT_NOTES.keys():
        return DICT_NOTES[key_name]

    

# @app.callback(Output('intermediate-value', 'data'),
#               [Input('btn-save-btn', 'n_clicks'), State("ipt-note", "value"),
#               State("video-player", "url"), State("dd-cut-scenes", "value")])
# def update_notes(n_clicks, note, url, cut_scene):
#     cut_scene = "" if cut_scene is None else cut_scene
#     url = "" if url is None else url

#     key_name = url + "-" + cut_scene
#     if key_name not in saved_note:
#         saved_note[key_name] = []
    
#     saved_note[key_name] += [note]
#     return saved_note


# @app.callback(Output('div-notes-holder', 'children'),
#               [Input('intermediate-value', 'data'),
#               Input("video-player", "url"), Input("dd-cut-scenes", "value")])
# def create_note_cards(saved_notes, url, cut_scene):
#     cut_scene = "" if cut_scene is None else cut_scene
#     url = "" if url is None else url
#     key_name = url + "-" + cut_scene

#     output_cards = []
#     print(saved_notes)
#     if key_name in saved_notes.keys():
#         for i in saved_notes[key_name]:
#             output_cards += [
#                 dbc.Row([
#                         dbc.Button("X", color="warning", className="mt-auto"),
#                         dbc.Card(dbc.CardBody(i))
#                     ])
#                 ]

#     return output_cards