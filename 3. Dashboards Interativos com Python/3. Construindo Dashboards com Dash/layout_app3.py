import dash
import dash_core_components as dcc
import dash_html_components as html

# https://dash.plotly.com/dash-core-components

# https://dash.plotly.com/dash-html-components

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Label('Dropdown'),
    dcc.Dropdown(
        options=[
            {'label': 'Rio Grande do Sul', 'value': 'NYC'},
            {'label': 'São Paulo', 'value': 'SP'},
            {'label': 'Santa Catarina', 'value': 'SC'}
        ],
        value='SP'
    ),

    html.Label('Multi-Select Dropdown'),
    dcc.Dropdown(
        options=[
            {'label': 'Rio Grande do Sul', 'value': 'NYC'},
            {'label': 'São Paulo', 'value': 'SP'},
            {'label': 'Santa Catarina', 'value': 'SC'}
        ],
        value=['SP', 'SC'],
        multi=True
    ),

    html.Label('Radio Items'),
    dcc.RadioItems(
        options=[
            {'label': 'Rio Grande do Sul', 'value': 'NYC'},
            {'label': 'São Paulo', 'value': 'SP'},
            {'label': 'Santa Catarina', 'value': 'SC'}
        ],
        value='SP'
    ),

    html.Label('Checkboxes'),
    dcc.Checklist(
        options=[
            {'label': 'Rio Grande do Sul', 'value': 'NYC'},
            {'label': 'São Paulo', 'value': 'SP'},
            {'label': 'Santa Catarina', 'value': 'SC'}
        ],
        value=['SP', 'SC']
    ),

    html.Label('Text Input'),
    dcc.Input(value='SP', type='text'),

    html.Label('Slider'),
    dcc.Slider(
        min=0,
        max=9,
        marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
        value=5,
    ),
], style={'columnCount': 2})

if __name__ == '__main__':
    app.run_server(debug=True)