# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 23:03:36 2025

@author: abhik
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import bcrypt
import sqlite3

dash.register_page(__name__, path='/reset_password')

layout = html.Div([
    html.H3("Reset Your Password"),
    dcc.Input(id='emp_id', type='text', placeholder='Employee ID'),
    dcc.Input(id='new_pass', type='password', placeholder='New Password'),
    dcc.Input(id='confirm_pass', type='password', placeholder='Confirm Password'),
    html.Button("Submit", id='submit_reset'),
    html.Div(id='reset_message', style={'color': 'red', 'marginTop': '10px'})
])

@callback(
    Output('reset_message', 'children'),
    Input('submit_reset', 'n_clicks'),
    State('emp_id', 'value'),
    State('new_pass', 'value'),
    State('confirm_pass', 'value'),
    prevent_initial_call=True
)
def reset_password(n, emp_id, new_pw, confirm_pw):
    if new_pw != confirm_pw:
        return "Passwords do not match."

    hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt())

    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE user_auth
        SET hashed_password = ?, must_change_password = 0
        WHERE employee_id = ?
    """, (hashed, emp_id))
    conn.commit()
    conn.close()

    return "✅ Password reset successful. Please login."
