import dash
from dash import Dash, html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import bcrypt
import sqlite3

# Initialize Dash
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# Connect to SQLite and build user_db dict
def build_user_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT employee_id FROM employee WHERE is_active = 1")
    users = cur.fetchall()
    conn.close()
    db = {}
    for (emp_id,) in users:
        hashed_pw = bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt())
        db[str(emp_id).strip()] = hashed_pw
    return db

user_db = build_user_db()

# Layout
app.layout = html.Div([
    dcc.Store(id='login-state', storage_type='session', data=False),
    html.H1("NERLDC Shift Substitute App", style={
        'textAlign': 'center',
        'color': '#1F3B4D',
        'fontFamily': 'Segoe UI, Roboto, Lato, sans-serif',
        'paddingTop': '20px',
        'fontWeight': 'bold'
    }),

    html.Div(
        html.Button('Logout', id='logout-btn', n_clicks=0, className='btn btn-danger'),
        style={'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px'}
    ),

    html.Div(
        id='login-form-container',
        children=[
            html.Div(id='login-form', children=[
                html.H3("Login to NERLDC Portal", style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}),
                dcc.Input(id='username', type='text', placeholder='Employee ID', debounce=True, className="form-control", style={'marginBottom': '10px'}),
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

    dash.page_container
])

# Callbacks
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
        uname = str(username).strip()
        if uname in user_db and bcrypt.checkpw(password.encode('utf-8'), user_db[uname]):
            return True, {'display': 'none'}, {'display': 'block'}, "", {'display': 'block'}, {'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px'}, "", "", login_clicks
        elif uname in user_db:
            return False, {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '70vh'}, {'display': 'none'}, "Invalid password", {'display': 'none'}, {'display': 'none'}, "", "", login_clicks
        else:
            return False, {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '70vh'}, {'display': 'none'}, "Employee ID not found", {'display': 'none'}, {'display': 'none'}, "", "", login_clicks

    if logged_in:
        return logged_in, {'display': 'none'}, {'display': 'block'}, "", {'display': 'block'}, {'display': 'flex', 'justifyContent': 'flex-end', 'padding': '10px'}, "", "", login_clicks
    else:
        return logged_in, {'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '70vh'}, {'display': 'none'}, "", {'display': 'none'}, {'display': 'none'}, "", "", login_clicks

# Run app
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run_server(host='0.0.0.0', port=port, debug=False)
