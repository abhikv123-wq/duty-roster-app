import dash
from dash import Dash, html, dcc, callback, Output, Input, State
from datetime import datetime, timedelta,date
import plotly.express as px
import dash_table as dt
import pandas as pd
from extract_data import  insert_employee, get_emp, get_employee_details, update_employee,delete_employee,update_employee_status
import os
from dash.exceptions import PreventUpdate
from dash import callback_context
import dash_bootstrap_components as dbc
import io
import calendar
dirname = os.path.dirname(__file__)

dash.register_page(__name__,path='/add_employee')

# Define the options for the Position dropdown
position_options = [
    {'label': 'SCM', 'value': '1'},
    {'label': '2&3', 'value': '2&3'},
    {'label': '4&5', 'value': '4&5'}
]

# Define the options for the Department dropdown
department_options = [
    {'label': 'SO', 'value': 'SO'},
    {'label': 'MO', 'value': 'MO'},
    {'label': 'CS', 'value': 'CS'},
    {'label': 'LO', 'value': 'LO'},
    {'label': 'IT', 'value': 'IT'}
]

# Define the options for the Duty Type dropdown
duty_type = [
    {'label': 'Shift Group A', 'value': 'A'},
    {'label': 'Shift Group B', 'value': 'B'},
    {'label': 'Shift Group C', 'value': 'C'},
    {'label': 'Shift Group D', 'value': 'D'},
    {'label': 'General', 'value': 'General'}
]
is_active = [
    {'label': 'Yes', 'value': 1},
    {'label': 'No', 'value': 0}
]
def get_list_emp():
    all_emp = get_emp()['name'].tolist()
    return [{'label': i, 'value': i} for i in all_emp]

def serve_layout():
    return html.Div([
        html.H2(children='Add New Employee', style={'textAlign': 'center', 'marginBottom': '20px'}),

        # Alert for feedback (hidden initially)
        dbc.Alert("This is a notification!", id="notf1", is_open=False, duration=5000,
                  style={'position': 'fixed', 'top': '5px', 'right': '5px', 'width': '200px', 'fontWeight': 'bold'}
        ),    
                # Alert for feedback (hidden initially)
        dbc.Alert("This is a notification!", id="notf2", is_open=False, duration=5000,
                  style={'position': 'fixed', 'top': '5px', 'right': '5px', 'width': '200px', 'fontWeight': 'bold'}
        ),  
                        # Alert for feedback (hidden initially)
        dbc.Alert("This is a notification!", id="notf3", is_open=False, duration=5000,
                  style={'position': 'fixed', 'top': '5px', 'right': '5px', 'width': '200px', 'fontWeight': 'bold'}
        ), 

        # Employee input fields wrapped in a Bootstrap grid
        dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Employee ID:"),
                    dbc.Input(id='empId-input', type='text', placeholder="Enter Employee ID", style={'width': '100%'})
                ], width=6),  # Adjust the width (50% of the screen)

                dbc.Col([
                    dbc.Label("Employee Name:"),
                    dbc.Input(id='name-input', type='text', placeholder="Enter name", style={'width': '100%'})
                ], width=6),  # Adjust the width (50% of the screen)
            ]),  # Removed form=True here

            dbc.Row([
                dbc.Col([
                    dbc.Label("Designation:"),
                    dbc.Input(id='designation-input', type='text', placeholder="Enter Designation", style={'width': '100%'})
                ], width=6),

                dbc.Col([
                    dbc.Label("Position:"),
                    dcc.Dropdown(
                        id='position-dropdown',
                        options=position_options,
                        placeholder="Select position",
                        style={'width': '100%'}
                    )
                ], width=6),
            ]),  # Removed form=True here

            dbc.Row([
                dbc.Col([
                    dbc.Label("Department:"),
                    dcc.Dropdown(
                        id='department-dropdown',
                        options=department_options,
                        placeholder="Select department",
                        style={'width': '100%'}
                    )
                ], width=6),

                dbc.Col([
                    dbc.Label("Duty Type:"),
                    dcc.Dropdown(
                        id='duty-dropdown',
                        options=duty_type,
                        placeholder="Select Duty Type (Shift / General)",
                        style={'width': '100%'}
                    )
                ], width=6),
            ]),  # Removed form=True here
            dbc.Row([
                dbc.Col([dbc.Label("Effective Date:"),  dcc.DatePickerSingle(id='effec_date',min_date_allowed=datetime.today(),initial_visible_month=datetime.today(),display_format='DD-MM-YYYY')], width=6),
            ]),  # Removed form=True here
            # Submit button with Bootstrap styling (adjusted width)
            dbc.Row([
                dbc.Col([
                    dbc.Button('Submit', id='add-emp', n_clicks=0, color="primary", size="lg", style={'width': '150px'})
                ], width=12),
            ], style={'marginTop': '20px'}),
        ]),
        html.H2(children='Update Employee Details', style={'textAlign': 'center', 'marginBottom': '20px'}),
        # Employee input fields wrapped in a Bootstrap grid
        dbc.Form([
            dbc.Row([
                dbc.Col([dbc.Label("Select Employee:"), dcc.Dropdown(id='emp-dropdown', options=[], placeholder="Select Employee", style={'width': '100%'})], width=6),
                dbc.Col([dbc.Label("Effective Date:"),  dcc.DatePickerSingle(id='effec_date-update',min_date_allowed=datetime.today(),initial_visible_month=datetime.today(),display_format='DD-MM-YYYY')], width=6),
            ]),

            # Employee details input fields
            dbc.Row([
                dbc.Col([dbc.Label("Employee ID:"), dbc.Input(id='empId-update', type='text', placeholder="Employee ID", style={'width': '100%'}, disabled=True)], width=6),
                dbc.Col([dbc.Label("Employee Name:"), dbc.Input(id='name-update', type='text', placeholder="Enter name", style={'width': '100%'})], width=6),
            ]),

            dbc.Row([
                dbc.Col([dbc.Label("Designation:"), dbc.Input(id='designation-update', type='text', placeholder="Enter Designation", style={'width': '100%'})], width=6),
                dbc.Col([dbc.Label("Position:"), dcc.Dropdown(id='position-dropdown-update', options=position_options, placeholder="Select position", style={'width': '100%'})], width=6),
            ]),

            dbc.Row([
                dbc.Col([dbc.Label("Department:"), dcc.Dropdown(id='department-dropdown-update', options=department_options, placeholder="Select department", style={'width': '100%'})], width=6),
                dbc.Col([dbc.Label("Duty Type:"), dcc.Dropdown(id='duty-dropdown-update', options=duty_type, placeholder="Select Duty Type (Shift / General)", style={'width': '100%'})], width=6),
            ]),

            dbc.Row([
                dbc.Col([dbc.Label("Is Active:"), dcc.Dropdown(id='is_active-update', options=is_active, placeholder="Is Active", style={'width': '100%'})], width=6),
            ]),
            # Update button with Bootstrap styling
            dbc.Row([
                dbc.Col([
                    dbc.Button('Update Employee', id='update-emp', n_clicks=0, color="primary", size="lg", style={'width': '200px'})], width=6),
                ],style={'marginTop': '20px'})

        ]),
        
    ])

layout = serve_layout

# Callback for handling form submission
@callback(
    Output('notf1', 'is_open'),  # Control alert visibility
    Output('notf1', 'children'),  # Control alert message
    Output("notf1", "color"),
    Input('add-emp', 'n_clicks'),
    State('empId-input', 'value'),
    State('name-input', 'value'),
    State('designation-input', 'value'),
    State('position-dropdown', 'value'),
    State('department-dropdown', 'value'),
    State('duty-dropdown', 'value'),
    State('effec_date', 'date'),
    prevent_initial_call=True
)
def handle_form_submission(n_clicks, emp_id, name, designation, position, department, duty_type,effec_date):
    if n_clicks > 0:
        if all([emp_id, name, designation, position, department, duty_type,effec_date]):
            # Process the form data (e.g., save to database, or perform any other action)
            if (position == 'SCM'):
                position = '1'
            insert_employee(emp_id, name, designation, position, department, duty_type,'1')
            update_employee_status(effec_date,name,'',duty_type)

            message = f"Employee {name} added successfully!"
            return True, message, 'success'  # Show success message
        else:
            return True, "Please fill out all fields!", 'danger' # Show error message

    return False, ""  # No feedback when form is not submitted yet

# Callback for dynamically updating employee list dropdown
@callback(
    Output('emp-dropdown', 'options'),
    Input('emp-dropdown', 'id')  # This triggers the callback to update dropdown when the page loads
)
def update_emp_dropdown(_):
    return get_list_emp()

# Callback to fetch selected employee's details
@callback(
    [Output('empId-update', 'value'),
     Output('name-update', 'value'),
     Output('designation-update', 'value'),
     Output('position-dropdown-update', 'value'),
     Output('department-dropdown-update', 'value'),
     Output('duty-dropdown-update', 'value'),
     Output('is_active-update', 'value')],
    Input('emp-dropdown', 'value')
)
def update_employee_details(emp_name):
    if emp_name:
        # Get the details of the employee based on the selected employee name
        employee_details = get_employee_details(emp_name)  # Implement this function to fetch employee details

        return (employee_details['employee_id'], employee_details['name'], employee_details['designation'], 
                employee_details['position'][0], employee_details['department'][0], employee_details['shift_group'][0],employee_details['is_active'][0])
    else:
        raise PreventUpdate

# Callback for handling employee update submission
@callback(
    Output('notf2', 'is_open'),
    Output('notf2', 'children'),
    Output("notf2", "color"),
    Input('update-emp', 'n_clicks'),
    State('empId-update', 'value'),
    State('name-update', 'value'),
    State('designation-update', 'value'),
    State('position-dropdown-update', 'value'),
    State('department-dropdown-update', 'value'),
    State('duty-dropdown-update', 'value'),
    State('effec_date-update', 'date'),
    State('is_active-update', 'value'),
    prevent_initial_call=True
)
def handle_update_submission(n_clicks, emp_id, name, designation, position, department, duty_type,effec_date,is_active):
    if n_clicks > 0:
        if all([emp_id, name, designation, position, department, duty_type,effec_date]):
            # Process the form data (e.g., update database)
            employee_details = get_employee_details(name[0])
            if (employee_details['is_active'][0] == 1 and is_active ==0):
                update_employee_status(effec_date,name[0],employee_details['shift_group'][0],'emp_removed')
            elif(employee_details['is_active'][0] == 0 and is_active == 1):
                update_employee_status(effec_date,name[0],'',duty_type)
            else:
                update_employee_status(effec_date,name[0],employee_details['shift_group'][0],duty_type)

            update_employee(emp_id, name[0], designation[0], position, department, duty_type,is_active) 

            message = f"Employee {name[0]} updated successfully!"
            return True, message, 'success'  # Show success message
        else:
            return True, "Please fill out all fields!", 'danger'  # Show error message

    return False, ""  # No feedback when form is not submitted yet
