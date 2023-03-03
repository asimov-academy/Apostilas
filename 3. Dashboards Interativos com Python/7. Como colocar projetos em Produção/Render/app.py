import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# ============ APP ============= #
app = dash.Dash(__name__)
server = app.server

# ======== Reading File ======== #
df = pd.read_csv('assets/data_sales.csv')

# =========  Layout  =========== #
app.layout = html.Div([
    html.H1("Sales Data Analysis"),

    html.H3("Filter by Category"),
    dcc.Dropdown(df['Category'].unique(), df['Category'].unique(), id='dropdown', multi=True),

    html.H3("Filter by Year"),
    dcc.Checklist([2017, 2018, 2019], [2017, 2018, 2019], id='checklist'),
    
    html.H2(id='message'),
    html.Hr(),

    dcc.Graph(id='histogram_graph'),
    dcc.Graph(id='sunburst_graph'),
    dcc.Graph(id='line_graph')
])

# ======== Callbacks ========== #
# Generating Graphs
@app.callback(
    Output('message', 'children'),
    Output('line_graph', 'figure'),
    Output('histogram_graph', 'figure'),
    Output('sunburst_graph', 'figure'),
    Input('checklist', 'value'),
    Input('dropdown', 'value'),
)
def generate_graphs(checklist, dropdown):
    if dropdown == [] or checklist == []:
        return ["Please insert values on the filters"], {}, {}, {} 
    else:
        df_aux = df[df['Category'].isin(dropdown)]
        df2 = df_aux[df_aux['Year'].isin(checklist)]

        df_line = df_aux.groupby(['Year', 'Category'])['Sales($)'].sum()
        df_line = pd.DataFrame(df_line).reset_index()

        line = px.line(df_line, x='Year', y='Sales($)', color='Category')
        line.update_layout(xaxis={'dtick':1})

        histogram = px.histogram(df2, x="Year", y="Sales($)", color='Category', barmode='group')
        sunburst = px.sunburst(df2, path=['Year', 'Category', 'Product'], values='Sales($)', height=700)

        return [], line, histogram, sunburst
    

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)
