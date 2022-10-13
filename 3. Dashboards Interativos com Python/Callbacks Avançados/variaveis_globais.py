from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd

app = Dash(__name__)

df = pd.DataFrame({
  'student_id' : range(1, 11),
  'score' : [1, 5, 2, 5, 2, 3, 1, 5, 1, 5]
})

app.layout = html.Div([
	dcc.Dropdown(list(range(1, 6)), 1, id='score'),
	'Foi pontuado pela seguinte quantidade de estudantes:',
	html.Div(id='output'),
    dcc.Store(id='store')
])

@app.callback(Output('store', 'data'), Input('score', 'value'))
def update_output(value):
	filtered_df = df[df['score'] == value]
	return filtered_df.to_dict()

@app.callback(Output('output', 'children'), Input('store', 'data'))
def update_output(data):
	filtered_df = pd.DataFrame(data)
	return len(filtered_df)


if __name__ == "__main__":
    app.run_server(debug=True)