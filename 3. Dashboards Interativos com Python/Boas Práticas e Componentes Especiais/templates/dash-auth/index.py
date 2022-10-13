from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import dash
from flask_login import current_user

from app import *
from pages import login, data, register


login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# =========  Layout  =========== #
app.layout = html.Div(children=[
                dbc.Row([
                        dbc.Col([
                            dcc.Location(id="base-url", refresh=False), 
                            dcc.Store(id="login-state", data=""),
                            dcc.Store(id="register-state", data=""),

                            html.Div(id="page-content", style={"height": "100vh", "display": "flex", "justify-content": "center"})
                        ]),
                    ])
            ], style={"padding": "0px"})


# =========  Callbacks Page1  =========== #
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.callback(Output("base-url", "pathname"), 
            [
                Input("login-state", "data"),
                Input("register-state", "data")
            ])
def render_page_content(login_state, register_state):
    ctx = dash.callback_context
    if ctx.triggered:
        trigg_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigg_id == 'login-state' and login_state == "success":
            return '/data'
        if trigg_id == 'login-state' and login_state == "error":
            return '/login'
        

        elif trigg_id == 'register-state':
            print(register_state, register_state=='')
            if register_state == "":
                return '/login'
            else:
                return '/register'
    else:
        return '/'


@app.callback(Output("page-content", "children"), 
            Input("base-url", "pathname"),
            [State("login-state", "data"), State("register-state", "data")])
def render_page_content(pathname, login_state, register_state):
    if (pathname == "/login" or pathname == "/"):
        return login.render_layout(login_state)

    if pathname == "/register":
        return register.render_layout(register_state)

    if pathname == "/data":
        if current_user.is_authenticated:
            return data.render_layout(current_user.username)
        else:
            return login.render_layout(register_state)
    
# Login and register buttons
# @app.callback(
#     Output('base-state', 'data'), 
    
#     [Input('login_button', 'n_clicks'),
#     Input('register-button', 'n_clicks')],  

#     [
#         State('user_login', 'value'), 
#         State('pwd_login', 'value'),
#         State('user_register', 'value'), 
#         State('pwd_register', 'value'),
#         State('email_register', 'value')
#     ])
# def successful(login_button, register, user_login, pwd_login, user_register, pwd_register, email_register):
#     print("hi")
#     return
    # user = Users.query.filter_by(username=username).first()
    # if user and password is not None:
    #     if check_password_hash(user.password, password):
    #         login_user(user)
    #         return '/data', ""
    #     else:
    #         return '/login', "error"
    # else:
    #     return '/login', "error"



# @app.callback(
#     [
#         Output('register-url', 'pathname'),
#         Output('register-state', 'data'), 
#     ],
#     Input('register-button', 'n_clicks'), 

#     [
#         State('user_register', 'value'), 
#         State('pwd_register', 'value'),
#         State('email_register', 'value')
#     ],
#     )
# def successful(n_clicks, username, password, email):
#     if n_clicks == None:
#         raise PreventUpdate

#     if username is not None and password is not None and email is not None:
#         hashed_password = generate_password_hash(password, method='sha256')
#         ins = Users_tbl.insert().values(username=username,  password=hashed_password, email=email)
#         conn = engine.connect()
#         conn.execute(ins)
#         conn.close()
#         return '/login', ''
#     else:
#         return '/register', 'error'

if __name__ == "__main__":
    app.run_server(port=8050, debug=True)