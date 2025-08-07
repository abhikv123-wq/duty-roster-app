import dash
from dash import Dash, html, dcc, callback, Output, Input, State
from datetime import datetime, timedelta,date
import plotly.express as px
from dash import dash_table as dt
import pandas as pd
from extract_data import employee_shift , insert_leave_details,get_leave_details,delete_leave
from statistics import mean 
import os
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


dash.register_page(__name__,path='/leave_details')

employee_shift_data = employee_shift()
data = [{'label': i, 'value': i} for i in employee_shift_data.name.tolist()]

def serve_layout():
    return html.Div([
    html.H2(children='Enter Leave Details of Shift Executive', style={'textAlign':'center'}),
    dbc.Alert("This is a notification!", id="notif_leave", is_open=False, duration=5000,
              style={'position': 'fixed', 'top': '5px', 'right': '5px', 'width': '200px','fontWeight': 'bold'}
), 
    dcc.Store(id='data-store-leave',data=update_leave_details().to_dict("records")),
    dcc.Dropdown(
        id='shift-list1',
        options=data,
        style={'zIndex': '10000', 'position': 'relative', 'marginTop': '20px'}  # Ensure it opens above the date picker

    ),
    dcc.DatePickerSingle(
        id='my-start-date',
        min_date_allowed=datetime.today(),
        initial_visible_month=datetime.today(),
        display_format='DD-MM-YYYY',
        placeholder='Start Date',
        style={'zIndex': '9999', 'position': 'relative'}
    ),
    dcc.DatePickerSingle(
        id='my-end-date',
        min_date_allowed=datetime.today(),
        initial_visible_month=datetime.today(),
        display_format='DD-MM-YYYY',
        placeholder='End Date',
        style={'zIndex': '9999', 'position': 'relative'}
    ),
    dbc.Button("Submit", 
                id="submit_leave",
                style={'fontSize': '18px', 
                    'fontWeight': 'bold', 
                    'color': '#ffffff', 
                    'backgroundColor': '#007bff', 
                    'borderRadius': '5px', 
                    'padding': '10px 20px',
                    'cursor': 'pointer'}),
    dbc.Alert("This is a notification!", id="notification2", is_open=False, duration=5000,
              style={'position': 'fixed', 'top': '5px', 'right': '5px', 'width': '200px','fontWeight': 'bold'}),    
    dcc.Store(id="button-clicked", data=False),
    html.Br(),
    html.H1(children='Applied Leave Details', style={'textAlign':'center'}),
        dcc.Loading(html.Div([
        dt.DataTable(
            id = 'leave-details', 
            columns = [
                        {'name': 'Employee Name', 'id': 'Employee Name'},
                        {'name': 'Date', 'id': 'Date'},
                        {'name': 'Delete Leave', 'id': 'Delete Leave', 'presentation': 'markdown'}
                    ],
            style_cell_conditional=[
                {'if': {'column_id': 'Date'}, 'width': '150px', 'textAlign': 'center'},
                {'if': {'column_id': 'Employee Name'}, 'width': '150px', 'textAlign': 'center'},
                {'if': {'column_id': 'Delete Leave'}, 'width': '150px', 'textAlign': 'center'}
            ],
            markdown_options={'link_target': '_self'},
            style_header={
                 'fontFamily': 'Arial',
                'fontSize': '20px',
                'fontWeight': 'bold',
                'color': '#ffffff',
                'backgroundColor': '#007bff'
            },
            style_data={
                'fontSize': '18px'  # Increase font size to 16px
            },
            style_table={'overflowY': 'scroll', 'height': '10000px'},
            style_cell={
                'height': '10px',
                'textAlign': 'center',
                'whiteSpace': 'pre-wrap'
            },
            fixed_rows={'headers': True}
        )   
    ]),type="default")

])
layout = serve_layout


@callback(
    [Output("notification2", "is_open"),
     Output("notification2", "children"),
     Output("notification2", "color")],
    State('my-start-date', 'date'),
    State('my-end-date', 'date'),
    Input("submit_leave", "n_clicks"),
    [State('shift-list1', 'value')],
    prevent_initial_call=True
)   
def leave_details(start_date,end_date,n_clicks,emp_name):

    if datetime.strptime(end_date,'%Y-%m-%d') >= datetime.strptime(start_date,'%Y-%m-%d'):
        total_days = datetime.strptime(end_date,'%Y-%m-%d') - datetime.strptime(start_date,'%Y-%m-%d')
        if emp_name is not None:
            for i in range(0,total_days.days+1):
                temp = datetime.strptime(start_date,'%Y-%m-%d') + timedelta(i)
                insert_leave_details(temp.date(),emp_name)
            return True,"Leave Details added successfully!", 'success'
        else:
            return True,"Please select Employee", 'danger'
    else:
        return True,"End Date Should be Greater than Start Date !!!", 'danger'

@callback(
    Output('leave-details', 'data'),
    Input('data-store-leave', 'data')
)
def update_table(data):
    return update_leave_details().to_dict("records")
 
def update_leave_details():
    data = get_leave_details()
    temp_df = pd.DataFrame(data)
    temp_df['date'] = pd.to_datetime(temp_df['date'])
    temp_df['date'] = temp_df['date'].dt.date

    leave_df = temp_df[temp_df['date'] > datetime.today().date()]

    temp_list = {'Employee Name' : [], 'Date':[]}
    temp_list['Employee Name'].extend(leave_df['emp_name'])
    temp_list['Date'].extend(leave_df['date'])

    temp_df = pd.DataFrame(temp_list)
    for i, row in temp_df.iterrows():
        temp_df.at[i, 'Delete Leave'] = f"[Delete Leave](#)"

    return temp_df


# Define a callback to handle button clicks
@callback(
    [Output("notif_leave", "is_open"),
     Output("notif_leave", "children"),
     Output("notif_leave", "color"),
     Output('data-store-leave', 'data')],
    [Input('leave-details', 'active_cell'),
    Input('leave-details', 'data')],
    prevent_initial_call=True
)
def handle_button_click(active_cell,data):
    if active_cell is not None:
        print("active_cell detected")
        row_index = active_cell['row']
        row_data = data[row_index]
        column_id = active_cell['column_id']
        if column_id.startswith('Delete Leave'):
            print(row_data)
            delete_leave(row_data['Employee Name'],row_data['Date'])
            temp_df = update_leave_details().to_dict("records")
            return True,"Leave Deleted!",'success',temp_df
    else:
        return False,'','info',update_leave_details().to_dict("records")


