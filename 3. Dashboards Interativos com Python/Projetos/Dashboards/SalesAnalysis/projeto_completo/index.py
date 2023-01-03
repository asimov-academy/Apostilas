import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
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
    "margin": {"l":10, "r":10, "t":10, "b":10}
}

config_graph={"displayModeBar": False, "showTips": False}

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY


# ===== Reading n cleaning File ====== #
df = pd.read_csv('dataset_asimov.csv')
df_cru = df.copy()

# Meses em numeros para poupar memória
df.loc[ df['Mês'] == 'Jan', 'Mês'] = 1
df.loc[ df['Mês'] == 'Fev', 'Mês'] = 2
df.loc[ df['Mês'] == 'Mar', 'Mês'] = 3
df.loc[ df['Mês'] == 'Abr', 'Mês'] = 4
df.loc[ df['Mês'] == 'Mai', 'Mês'] = 5
df.loc[ df['Mês'] == 'Jun', 'Mês'] = 6
df.loc[ df['Mês'] == 'Jul', 'Mês'] = 7
df.loc[ df['Mês'] == 'Ago', 'Mês'] = 8
df.loc[ df['Mês'] == 'Set', 'Mês'] = 9
df.loc[ df['Mês'] == 'Out', 'Mês'] = 10
df.loc[ df['Mês'] == 'Nov', 'Mês'] = 11
df.loc[ df['Mês'] == 'Dez', 'Mês'] = 12

# Algumas limpezas
df['Valor Pago'] = df['Valor Pago'].str.lstrip('R$ ')
df.loc[df['Status de Pagamento'] == 'Pago', 'Status de Pagamento'] = 1
df.loc[df['Status de Pagamento'] == 'Não pago', 'Status de Pagamento'] = 0

# Transformando em int tudo que der
df['Chamadas Realizadas'] = df['Chamadas Realizadas'].astype(int)
df['Dia'] = df['Dia'].astype(int)
df['Mês'] = df['Mês'].astype(int)
df['Valor Pago'] = df['Valor Pago'].astype(int)
df['Status de Pagamento'] = df['Status de Pagamento'].astype(int)


# Criando opções pros filtros que virão
options_month = [{'label': 'Ano todo', 'value': 0}]
for i, j in zip(df_cru['Mês'].unique(), df['Mês'].unique()):
    options_month.append({'label': i, 'value': j})
options_month = sorted(options_month, key=lambda x: x['value']) 

options_team = [{'label': 'Todas Equipes', 'value': 0}]
for i in df['Equipe'].unique():
    options_team.append({'label': i, 'value': i})
# ========= Função dos Filtros ========= #
def month_filter(month):
    if month == 0:
        mask = df['Mês'].isin(df['Mês'].unique())
    else:
        mask = df['Mês'].isin([month])
    return mask

def team_filter(team):
    if team == 0:
        mask = df['Equipe'].isin(df['Equipe'].unique())
    else:
        mask = df['Equipe'].isin([team])
    return mask

def convert_to_text(month):
    match month:
        case 0:
            x = 'Ano Todo'
        case 1:
            x = 'Janeiro'
        case 2:
            x = 'Fevereiro'
        case 3:
            x = 'Março'
        case 4:
            x = 'Abril'
        case 5:
            x = 'Maio'
        case 6:
            x = 'Junho'
        case 7:
            x = 'Julho'
        case 8:
            x = 'Agosto'
        case 9:
            x = 'Setembro'
        case 10:
            x = 'Outubro'
        case 11:
            x = 'Novembro'
        case 12:
            x = 'Dezembro'
    return x


# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    # Armazenamento de dataset
    # dcc.Store(id='dataset', data=df_store),

    # Layout
    # Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([  
                            html.Legend("Sales Analytics")
                        ], sm=8),
                        dbc.Col([        
                            html.I(className='fa fa-balance-scale', style={'font-size': '300%'})
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
                    dbc.Row(
                        dbc.Col(
                            html.Legend('Top Consultores por Equipe')
                        )
                    ),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='graph1', className='dbc', config=config_graph)
                        ], sm=12, md=7),
                        dbc.Col([
                            dcc.Graph(id='graph2', className='dbc', config=config_graph)
                        ], sm=12, lg=5)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=7),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row(
                        dbc.Col([
                            html.H5('Escolha o Mês'),
                            dbc.RadioItems(
                                id="radio-month",
                                options=options_month,
                                value=0,
                                inline=True,
                                labelCheckedClassName="text-success",
                                inputCheckedClassName="border border-success bg-success",
                            ),
                            html.Div(id='month-select', style={'text-align': 'center', 'margin-top': '30px'}, className='dbc')
                        ])
                    )
                ])
            ], style=tab_card)
        ], sm=12, lg=3)
    ], className='g-2 my-auto', style={'margin-top': '7px'}),

    # Row 2
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph3', className='dbc', config=config_graph)
                        ])
                    ], style=tab_card)
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph4', className='dbc', config=config_graph)
                        ])
                    ], style=tab_card)
                ])
            ], className='g-2 my-auto', style={'margin-top': '7px'})
        ], sm=12, lg=5),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph5', className='dbc', config=config_graph)    
                        ])
                    ], style=tab_card)
                ], sm=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='graph6', className='dbc', config=config_graph)    
                        ])
                    ], style=tab_card)
                ], sm=6)
            ], className='g-2'),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dcc.Graph(id='graph7', className='dbc', config=config_graph)
                    ], style=tab_card)
                ])
            ], className='g-2 my-auto', style={'margin-top': '7px'})
        ], sm=12, lg=4),
        dbc.Col([
            dbc.Card([
                dcc.Graph(id='graph8', className='dbc', config=config_graph)
            ], style=tab_card)
        ], sm=12, lg=3)
    ], className='g-2 my-auto', style={'margin-top': '7px'}),
    
    # Row 3
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4('Distribuição de Propaganda'),
                    dcc.Graph(id='graph9', className='dbc', config=config_graph)
                ])
            ], style=tab_card)
        ], sm=12, lg=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Valores de Propaganda convertidos por mês"),
                    dcc.Graph(id='graph10', className='dbc', config=config_graph)
                ])
            ], style=tab_card)
        ], sm=12, lg=5),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='graph11', className='dbc', config=config_graph)
                ])
            ], style=tab_card)
        ], sm=12, lg=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5('Escolha a Equipe'),
                    dbc.RadioItems(
                        id="radio-team",
                        options=options_team,
                        value=0,
                        inline=True,
                        labelCheckedClassName="text-warning",
                        inputCheckedClassName="border border-warning bg-warning",
                    ),
                    html.Div(id='team-select', style={'text-align': 'center', 'margin-top': '30px'}, className='dbc')
                ])
            ], style=tab_card)
        ], sm=12, lg=2),
    ], className='g-2 my-auto', style={'margin-top': '7px'})
], fluid=True, style={'height': '100vh'})


# ======== Callbacks ========== #
# Graph 1 and 2
@app.callback(
    Output('graph1', 'figure'),
    Output('graph2', 'figure'),
    Output('month-select', 'children'),
    Input('radio-month', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph1(month, toggle):
    template = template_theme1 if toggle else template_theme2

    mask = month_filter(month)
    df_1 = df.loc[mask]

    df_1 = df_1.groupby(['Equipe', 'Consultor'])['Valor Pago'].sum()
    df_1 = df_1.sort_values(ascending=False)
    df_1 = df_1.groupby('Equipe').head(1).reset_index()

    fig2 = go.Figure(go.Pie(labels=df_1['Consultor'] + ' - ' + df_1['Equipe'], values=df_1['Valor Pago'], hole=.6))
    fig1 = go.Figure(go.Bar(x=df_1['Consultor'], y=df_1['Valor Pago'], textposition='auto', text=df_1['Valor Pago']))
    fig1.update_layout(main_config, height=200, template=template)
    fig2.update_layout(main_config, height=200, template=template, showlegend=False)

    select = html.H1(convert_to_text(month))

    return fig1, fig2, select

# Graph 3
@app.callback(
    Output('graph3', 'figure'),
    Input('radio-team', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph3(team, toggle):
    template = template_theme1 if toggle else template_theme2

    mask = team_filter(team)
    df_3 = df.loc[mask]

    df_3 = df_3.groupby('Dia')['Chamadas Realizadas'].sum().reset_index()
    fig3 = go.Figure(go.Scatter(
    x=df_3['Dia'], y=df_3['Chamadas Realizadas'], mode='lines', fill='tonexty'))
    fig3.add_annotation(text='Chamadas Médias por dia do Mês',
        xref="paper", yref="paper",
        font=dict(
            size=17,
            color='gray'
            ),
        align="center", bgcolor="rgba(0,0,0,0.8)",
        x=0.05, y=0.85, showarrow=False)
    fig3.add_annotation(text=f"Média : {round(df_3['Chamadas Realizadas'].mean(), 2)}",
        xref="paper", yref="paper",
        font=dict(
            size=20,
            color='gray'
            ),
        align="center", bgcolor="rgba(0,0,0,0.8)",
        x=0.05, y=0.55, showarrow=False)

    fig3.update_layout(main_config, height=180, template=template)
    return fig3

# Graph 4
@app.callback(
    Output('graph4', 'figure'),
    Input('radio-team', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph4(team, toggle):
    template = template_theme1 if toggle else template_theme2
    
    mask = team_filter(team)
    df_4 = df.loc[mask]

    df_4 = df_4.groupby('Mês')['Chamadas Realizadas'].sum().reset_index()
    fig4 = go.Figure(go.Scatter(x=df_4['Mês'], y=df_4['Chamadas Realizadas'], mode='lines', fill='tonexty'))

    fig4.add_annotation(text='Chamadas Médias por Mês',
        xref="paper", yref="paper",
        font=dict(
            size=15,
            color='gray'
            ),
        align="center", bgcolor="rgba(0,0,0,0.8)",
        x=0.05, y=0.85, showarrow=False)
    fig4.add_annotation(text=f"Média : {round(df_4['Chamadas Realizadas'].mean(), 2)}",
        xref="paper", yref="paper",
        font=dict(
            size=20,
            color='gray'
            ),
        align="center", bgcolor="rgba(0,0,0,0.8)",
        x=0.05, y=0.55, showarrow=False)

    fig4.update_layout(main_config, height=180, template=template)
    return fig4

# Indicators 1 and 2 ------ Graph 5 and 6
@app.callback(
    Output('graph5', 'figure'),
    Output('graph6', 'figure'),
    Input('radio-month', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph5(month, toggle):
    template = template_theme1 if toggle else template_theme2

    mask = month_filter(month)
    df_5 = df_6 = df.loc[mask]
    
    df_5 = df_5.groupby(['Consultor', 'Equipe'])['Valor Pago'].sum()
    df_5.sort_values(ascending=False, inplace=True)
    df_5 = df_5.reset_index()
    fig5 = go.Figure()
    fig5.add_trace(go.Indicator(mode='number+delta',
        title = {"text": f"<span>{df_5['Consultor'].iloc[0]} - Top Consultant</span><br><span style='font-size:70%'>Em vendas - em relação a média</span><br>"},
        value = df_5['Valor Pago'].iloc[0],
        number = {'prefix': "R$"},
        delta = {'relative': True, 'valueformat': '.1%', 'reference': df_5['Valor Pago'].mean()}
    ))

    df_6 = df_6.groupby('Equipe')['Valor Pago'].sum()
    df_6.sort_values(ascending=False, inplace=True)
    df_6 = df_6.reset_index()
    fig6 = go.Figure()
    fig6.add_trace(go.Indicator(mode='number+delta',
        title = {"text": f"<span>{df_6['Equipe'].iloc[0]} - Top Team</span><br><span style='font-size:70%'>Em vendas - em relação a média</span><br>"},
        value = df_6['Valor Pago'].iloc[0],
        number = {'prefix': "R$"},
        delta = {'relative': True, 'valueformat': '.1%', 'reference': df_6['Valor Pago'].mean()}
    ))

    fig5.update_layout(main_config, height=200, template=template)
    fig6.update_layout(main_config, height=200, template=template)
    fig5.update_layout({"margin": {"l":0, "r":0, "t":20, "b":0}})
    fig6.update_layout({"margin": {"l":0, "r":0, "t":20, "b":0}})
    return fig5, fig6

# Graph 7
@app.callback(
    Output('graph7', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph7(toggle):
    template = template_theme1 if toggle else template_theme2

    df_7 = df.groupby(['Mês', 'Equipe'])['Valor Pago'].sum().reset_index()
    df_7_group = df.groupby('Mês')['Valor Pago'].sum().reset_index()
    
    fig7 = px.line(df_7, y="Valor Pago", x="Mês", color="Equipe")
    fig7.add_trace(go.Scatter(y=df_7_group["Valor Pago"], x=df_7_group["Mês"], mode='lines+markers', fill='tonexty', name='Total de Vendas'))

    fig7.update_layout(main_config, yaxis={'title': None}, xaxis={'title': None}, height=190, template=template)
    fig7.update_layout({"legend": {"yanchor": "top", "y":0.99, "font" : {"color":"white", 'size': 10}}})
    return fig7

# Graph 8
@app.callback(
    Output('graph8', 'figure'),
    Input('radio-month', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph8(month, toggle):
    template = template_theme1 if toggle else template_theme2

    mask = month_filter(month)
    df_8 = df.loc[mask]

    df_8 = df_8.groupby('Equipe')['Valor Pago'].sum().reset_index()
    fig8 = go.Figure(go.Bar(
        x=df_8['Valor Pago'],
        y=df_8['Equipe'],
        orientation='h',
        textposition='auto',
        text=df_8['Valor Pago'],
        insidetextfont=dict(family='Times', size=12)))

    fig8.update_layout(main_config, height=360, template=template)
    return fig8

# Graph 9
@app.callback(
    Output('graph9', 'figure'),
    Input('radio-month', 'value'),
    Input('radio-team', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph9(month, team, toggle):
    template = template_theme1 if toggle else template_theme2

    mask = month_filter(month)
    df_9 = df.loc[mask]

    mask = team_filter(team)
    df_9 = df_9.loc[mask]

    df_9 = df_9.groupby('Meio de Propaganda')['Valor Pago'].sum().reset_index()

    fig9 = go.Figure()
    fig9.add_trace(go.Pie(labels=df_9['Meio de Propaganda'], values=df_9['Valor Pago'], hole=.7))

    fig9.update_layout(main_config, height=150, template=template, showlegend=False)
    return fig9

# Graph 10
@app.callback(
    Output('graph10', 'figure'),
    Input('radio-team', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph10(team, toggle):
    template = template_theme1 if toggle else template_theme2
    
    mask = team_filter(team)
    df_10 = df.loc[mask]

    df10 = df_10.groupby(['Meio de Propaganda', 'Mês'])['Valor Pago'].sum().reset_index()
    fig10 = px.line(df10, y="Valor Pago", x="Mês", color="Meio de Propaganda")

    fig10.update_layout(main_config, height=200, template=template, showlegend=False)
    return fig10

# Graph 11
@app.callback(
    Output('graph11', 'figure'),
    Output('team-select', 'children'),
    Input('radio-month', 'value'),
    Input('radio-team', 'value'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def graph11(month, team, toggle):
    template = template_theme1 if toggle else template_theme2

    mask = month_filter(month)
    df_11 = df.loc[mask]

    mask = team_filter(team)
    df_11 = df_11.loc[mask]

    fig11 = go.Figure()
    fig11.add_trace(go.Indicator(mode='number',
        title = {"text": f"<span style='font-size:150%'>Valor Total</span><br><span style='font-size:70%'>Em Reais</span><br>"},
        value = df_11['Valor Pago'].sum(),
        number = {'prefix': "R$"}
    ))

    fig11.update_layout(main_config, height=300, template=template)
    select = html.H1("Todas Equipes") if team == 0 else html.H1(team)

    return fig11, select


# Run server
if __name__ == '__main__':
    app.run_server(debug=False)
