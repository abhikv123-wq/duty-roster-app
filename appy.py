import dash
from dash import Dash, html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import bcrypt

# Use a clean and vibrant theme
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])

# Simple user database
user_db = {
    "admin": bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt())
}

# Main layout
app.layout = html.Div([
    dcc.Store(id='login-state', storage_type='session', data=False),

    html.Div([
        html.H1("NERLDC Shift Substitute App", style={
            'textAlign': 'center',
            'color': '#1F3B4D',
            'fontFamily': 'Segoe UI, Roboto, Lato, sans-serif',
            'paddingTop': '20px',
            'fontWeight': 'bold'
        }),
    ]),

    html.Div(
        html.Button('Logout', id='logout-btn', n_clicks=0, className='btn btn-danger'),
        style={'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px'}
    ),

    html.Div(
        id='login-form-container',
        children=[
            html.Div(id='login-form', children=[
                html.H3("Login to NERLDC Portal", style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}),
                dcc.Input(id='username', type='text', placeholder='Username', debounce=True, className="form-control", style={'marginBottom': '10px'}),
                dcc.Input(id='password', type='password', placeholder='Password', debounce=True, className="form-control", style={'marginBottom': '10px'}),
                html.Button('Login', id='login-btn', n_clicks=0, className='btn btn-primary btn-block', style={'width': '100%'}),
                html.Div(id='error-message', style={'color': 'red', 'marginTop': '10px'})
            ], style={'width': '300px'})
        ],
        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '70vh'}
    ),

    html.Div(id='dashboard', children=[
        html.Div([
            html.A('Shift Roster', href='/', className='btn btn-outline-info mx-1'),
            html.A('Submit Leave Details', href='/leave_details', className='btn btn-outline-info mx-1'),
            html.A('Shift Substitute', href='/shift_substitute', className='btn btn-outline-info mx-1'),
            html.A('Assigned Substitute', href='/assigned_substitute', className='btn btn-outline-info mx-1'),
            html.A('Substitute Data', href='/substitute_employee_data', className='btn btn-outline-info mx-1'),
            html.A('Add / Edit Employee', href='/add_employee', className='btn btn-outline-info mx-1'),
        ], className="d-flex justify-content-center my-3")
    ], style={'display': 'none'}),

    dash.page_container  # Page-specific content
])

# Callback for login/logout
@app.callback(
    [Output('login-state', 'data'),
     Output('login-form-container', 'style'),
     Output('dashboard', 'style'),
     Output('error-message', 'children'),
     Output(dash.page_container, 'style'),
     Output('logout-btn', 'style'),
     Output('username', 'value'),
     Output('password', 'value'),
     Output('logout-btn', 'n_clicks')],
    [Input('login-btn', 'n_clicks'),
     Input('logout-btn', 'n_clicks')],
    [State('username', 'value'),
     State('password', 'value'),
     State('login-state', 'data')]
)
def login_logout_handler(login_clicks, logout_clicks, username, password, logged_in):
    if logout_clicks > 0:
        return False, {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '70vh'}, {'display': 'none'}, "", {'display': 'none'}, {'display': 'none'}, "", "", 0

    if login_clicks > 0 and username and password:
        if username in user_db and bcrypt.checkpw(password.encode('utf-8'), user_db[username]):
            return True, {'display': 'none'}, {'display': 'block'}, "", {'display': 'block'}, {'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px'}, "", "", login_clicks
        elif username in user_db:
            return False, {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '70vh'}, {'display': 'none'}, "Invalid password", {'display': 'none'}, {'display': 'none'}, "", "", login_clicks
        else:
            return False, {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '70vh'}, {'display': 'none'}, "Username not found", {'display': 'none'}, {'display': 'none'}, "", "", login_clicks

    if logged_in:
        return logged_in, {'display': 'none'}, {'display': 'block'}, "", {'display': 'block'}, {'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px'}, "", "", login_clicks
    else:
        return logged_in, {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '70vh'}, {'display': 'none'}, "", {'display': 'none'}, {'display': 'none'}, "", "", login_clicks

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8086, debug=False)
