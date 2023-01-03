import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# import from folders/theme changer
from app import *
from dash_bootstrap_templates import ThemeSwitchAIO


# ========== Styles ============ #
tab_card = {'height': '100%'}

main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":0.9, 
                "xanchor":"left",
                "x":0.1,
                "title": {"text": None},
                "font" :{"color":"white"},
                "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l":0, "r":0, "t":20, "b":0}
}

template_theme1 = "zephyr"
template_theme2 = "solar"
url_theme1 = dbc.themes.ZEPHYR
url_theme2 = dbc.themes.SOLAR


# ===== Reading n cleaning File ====== #
# Quando for gravar a aula, explicar todas as alterações no Jupyter lab e depois só colar pra cá.
df = pd.read_csv("vgsales.csv")

# TRATAR O DATAFRAME EM AULA (Jupyter) ANTES DE PARTIR PRO CÓDIGO !!!!!
# df.isnull().sum()

# Excluindo dados vazios
df.dropna(inplace=True)

# Dropando a coluna de Rank
df.drop('Rank', axis=1, inplace=True)

# A partir de 2017 os valores começam a ser faltantes, então vamos deixar o df só até 2017. Notando que não tem 2018 e 19, então tiramos 20
df = df[df['Year'] != 2020]

# Transformando a coluna de ano em integer
df['Year'] = df['Year'].astype('int')

# Separando Generos + Global
global_genres = df.groupby(['Genre'])['Global_Sales'].sum().sort_values(ascending=False).reset_index()['Genre'].unique().tolist()
global_genres.insert(0, 'Global')

# Criando outros dfs derivados do principal
top_publishers = df.groupby(['Publisher'])['Global_Sales'].sum()
top_publishers = top_publishers.sort_values(ascending=False).head(10).reset_index()

# To dict - para salvar no dcc.store
df_store = df.to_dict()


# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    # Armazenamento de dataset
    dcc.Store(id='dataset', data=df_store),

    # Layout
    # Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([  
                            html.Legend("Game Sales Metrics")
                        ], sm=8),
                        dbc.Col([         
                            html.I(className='fa fa-gamepad', style={'font-size': '300%'})
                        ], sm=4, align="center")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
                            html.Legend("Asimov Academy")
                        ])
                    ], style={'margin-top': '10px'}),
                    dbc.Row([
                        dbc.Button("Visite o Site", href="https://asimov.academy/", target="_blank")
                    ], style={'margin-top': '10px'})
                ])
            ], style=tab_card)
        ], sm=4, lg=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='graph0', className='dbc', config={"displayModeBar": False, "showTips": False})
                ])
            ], style=tab_card)
        ], sm=12, lg=10)
    ], className='g-2 my-auto', style={'margin-top': '7px'}),
    
    # Row Single Card
    dbc.Row([
        dbc.Col([
            dbc.Card([                
                dbc.Row([
                    dbc.Col([
                        dcc.RangeSlider(
                            id='rangeslider',
                            marks= {int(x): f'{x}' for x in df['Year'].unique()},
                            step=3,                
                            min=1980,
                            max=2017,
                            value=[1980,2017],   
                            dots=True,             
                            pushable=3,
                            tooltip={'always_visible':False, 'placement':'bottom'},
                        )
                    ], sm=12, style={'margin-top': '15px'}),
                    # componente invisivel
                    dcc.Interval(id='interval', interval=10000),
                ], className='g-1', style={'height': '20%', 'justify-content': 'center'}) 
            ], style=tab_card)
        ])
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    # Row 3
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Top 10 em valor de venda, em milhões"),
                    dcc.Graph(id='graph1', className='dbc', config={"displayModeBar": False, "showTips": False})
                ])
            ], style=tab_card)
        ], sm=12, lg=4, style={'margin-top': '7px'}),
        # Card 2
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph2', className='dbc', config={"displayModeBar": False, "showTips": False})
                        ])
                    ], style=tab_card)
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='graph3', className='dbc', config={"displayModeBar": False, "showTips": False})
                            ])
                        ])
                    ], style=tab_card)
                ], sm=12, lg=4),
                dbc.Col([
                    dbc.Card([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='graph4', className='dbc',  config={"displayModeBar": False, "showTips": False})
                            ])
                        ])
                    ], style=tab_card)
                ], sm=12, lg=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H5('Filtro por Gênero'),
                                    dbc.RadioItems(
                                        id="radio-genre",
                                        options=[{"label": x, "value": x} for x in global_genres],
                                        value='Global',
                                        inline=True,
                                        labelCheckedClassName="text-success",
                                        inputCheckedClassName="border border-success bg-success",
                                    ),
                               ])
                            ])
                        ])
                    ], style=tab_card)
                ], sm=12, lg=4)
            ], className='g-2 my-auto')
        ], sm=12, lg=8)
    ], justify='center', className='g-2 my-auto'),
], fluid=True, style={'height': '100vh'})


# ======== Callbacks ========== #
# Pie Charts
@app.callback(
    Output('graph0', 'figure'),
    Input('rangeslider', 'value'),
    Input('radio-genre', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
    )
def graph0(date, radio, toggle):
    template = template_theme1 if toggle else template_theme2

    if radio == 'Global':
        mask = (df['Year'] >= date[0]) & (df['Year'] <= date[1])
    else:
        mask = (df['Year'] >= date[0]) & (df['Year'] <= date[1]) & (df['Genre'].isin([radio]))
    
    df_subplot = df.loc[mask]

    df_NA = df_subplot.sort_values(by='NA_Sales', ascending=False).head(6).rename(columns = {'NA_Sales': 'Sales'})
    df_EU = df_subplot.sort_values(by='EU_Sales', ascending=False).head(6).rename(columns = {'EU_Sales': 'Sales'})
    df_JP = df_subplot.sort_values(by='JP_Sales', ascending=False).head(6).rename(columns = {'JP_Sales': 'Sales'})
    df_Other = df_subplot.sort_values(by='Other_Sales', ascending=False).head(6).rename(columns = {'Other_Sales': 'Sales'})

    subplot_topgames = make_subplots(rows=1, cols=4, specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}, {"type": "pie"}]],  subplot_titles=("América do Norte", "Europa", "Japão", "Outras Regiões"))

    subplot_topgames.add_trace(go.Pie(
        labels=df_NA['Name'], values=df_NA['Sales'], hole=.2), row=1, col=1)
    subplot_topgames.add_trace(go.Pie(
        labels=df_EU['Name'], values=df_EU['Sales'], hole=.2), row=1, col=2)
    subplot_topgames.add_trace(go.Pie(
        labels=df_JP['Name'], values=df_JP['Sales'], hole=.2), row=1, col=3)
    subplot_topgames.add_trace(go.Pie(
        labels=df_Other['Name'], values=df_Other['Sales'], hole=.2), row=1, col=4)

    subplot_topgames.update_layout(margin={"l":0, "r":0, "t":20, "b":0}, height=200, template=template)

    return subplot_topgames

# Graph1 - Horizontal Bars
@app.callback(
    Output('graph1', 'figure'),
    Input('rangeslider', 'value'),
    Input('radio-genre', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def fig1(date, radio, toggle):
    template = template_theme1 if toggle else template_theme2
    if radio == 'Global':
        mask = (df['Year'] >= date[0]) & (df['Year'] <= date[1])
    else:
        mask = (df['Year'] >= date[0]) & (df['Year'] <= date[1]) & (df['Genre'].isin([radio]))
    
    
    #radio = 'Action'
    #date = [1980, 2017]
    
    
    df_topglobal = df.loc[mask]
    df_topglobal = df_topglobal.head(10).sort_values(by='Global_Sales', ascending=True)
    text = [f'{x} - U${y} milhões' for x,y in zip(df_topglobal['Name'].unique(), df_topglobal['Global_Sales'].unique())]

    fig = go.Figure(go.Bar(x=df_topglobal['Global_Sales'], y=df_topglobal['Name'], orientation='h', text=text))
    fig.update_layout(main_config, height=410, xaxis={'title': None, 'showticklabels':False}, yaxis={'title': None, 'showticklabels':False}, template=template)
    return fig


# Graph 2 - Line Chart
@app.callback(
    Output('graph2', 'figure'),
    Input('rangeslider', 'value'),
    Input('radio-genre', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
    )
def long(date, radio, toggle):
    template = template_theme1 if toggle else template_theme2
    if radio == 'Global':
        mask = (df['Year'] >= date[0]) & (df['Year'] <= date[1])
    else:
        mask = (df['Year'] >= date[0]) & (df['Year'] <= date[1]) & (df['Genre'].isin([radio]))

    df_anos = df.loc[mask]

    trace = df_anos.groupby('Year')['Global_Sales'].sum().reset_index()

    fig_anos = go.Figure(go.Scatter(x=trace['Year'], y=trace['Global_Sales'], mode='lines+markers', fill='tonexty', name='Global Sales'))
    fig_anos.update_layout(main_config, height=200, xaxis={'title': None}, yaxis={'title': None}, template=template)

    fig_anos.add_annotation(text=f'Vendas em milhões de {date[0]} a {date[1]}',
        xref="paper", yref="paper",
        font=dict(
            size=20,
            color='gray'
            ),
        align="center", bgcolor="rgba(0,0,0,0.8)", opacity=0.8,
        x=0.05, y=0.85, showarrow=False)

    return fig_anos

# Indicator 1 and 2
@app.callback(
    Output('graph3', 'figure'),
    Output('graph4', 'figure'),
    Input('rangeslider', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def ind1(date, toggle):
    template = template_theme1 if toggle else template_theme2
    
    mask = (df['Year'] >= date[0]) & (df['Year'] <= date[1])

    df_graph3 = df_graph4 = df.loc[mask]

    df_graph3 = df_graph3.groupby(['Publisher'])['Global_Sales'].sum().reset_index()
    df_graph4 = df_graph4.groupby(['Genre'])['Global_Sales'].sum().reset_index()
    
    value1 = df_graph3['Global_Sales'].max()
    name1 = df_graph3.loc[df_graph3['Global_Sales'].idxmax()]['Publisher']

    value2 = df_graph4['Global_Sales'].max()
    name2 = df_graph4.loc[df_graph4['Global_Sales'].idxmax()]['Genre']

    fig1 = go.Figure()
    fig2 = go.Figure()
    
    fig1.add_trace(go.Indicator(
        mode = "number",
        title = {"text": f"<span style='font-size:150%'>{name1} - Top Seller</span><br><span style='font-size:70%'>Em milhões de dólares</span><br><span style='font-size:0.7em'>{date[0]} - {date[1]}</span>"},
        value = value1,
        number = {'valueformat': '.2f'}
    ))

    fig2.add_trace(go.Indicator(
        mode = "number",
        title = {"text": f"<span style='font-size:150%'>{name2} - Top Genre</span><br><span style='font-size:70%'>Em milhões de dólares</span><br><span style='font-size:0.7em'>{date[0]} - {date[1]}</span>"},
        value = value2,
        number = {'valueformat': '.2f'}
    ))

    fig1.update_layout(main_config, height=273, template=template)
    fig2.update_layout(main_config, height=273, template=template)

    return fig1, fig2



# Run server
if __name__ == '__main__':
    app.run_server(debug=False)
