import dash
from dash import html, dcc, Input, Output, ctx

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button('Button 1', id='btn-1-ctx-example'),
    html.Button('Button 2', id='btn-2-ctx-example'),
    html.Button('Button 3', id='btn-3-ctx-example'),
    html.Div(id='container-ctx-example')
])


@app.callback(Output('container-ctx-example','children'),
              Input('btn-1-ctx-example', 'n_clicks'),
              Input('btn-2-ctx-example', 'n_clicks'),
              Input('btn-3-ctx-example', 'n_clicks'))
def display(btn1, btn2, btn3):
    button_clicked = triggered_id
    return html.Div([
        dcc.Markdown(
            f'''You last clicked button with ID {button_clicked}
            ''' if button_clicked else '''You haven't clicked any button yet''')
    ])

if __name__ == '__main__':
    app.run_server(debug=True)