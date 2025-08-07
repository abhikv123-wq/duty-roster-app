import dash
from dash import Dash, html, dcc, callback, Output, Input, State
from datetime import datetime, timedelta,date
import plotly.express as px
import dash_table as dt
import pandas as pd
from extract_data import confirm_substitute,get_substitute_list,deny_substitute,get_sub_list
import os
from dash.exceptions import PreventUpdate
from dash import callback_context
import dash_bootstrap_components as dbc
import io
import calendar
dirname = os.path.dirname(__file__)
filename = os.path.join('pages', 'config', 'Data.xlsx')

dash.register_page(__name__,path='/assigned_substitute')
df = pd.read_excel(filename,sheet_name='shifts')

def serve_layout():
    return html.Div([
    html.H2(children='Assigned Substitute', style={'textAlign':'center'}),
    dbc.Alert("This is a notification!", id="notification", is_open=False, duration=5000,
              style={'position': 'fixed', 'top': '5px', 'right': '5px', 'width': '200px','fontWeight': 'bold'}
),    
    dcc.Store(id='data-store',data=get_sub_data().to_dict("records")),
    dcc.DatePickerRange(
        id='date-range',
        initial_visible_month= datetime.today(),
        display_format='DD-MM-YYYY',
        start_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        end_date=datetime(datetime.today().year, datetime.today().month, calendar.monthrange(datetime.today().year, datetime.today().month)[1]).strftime('%Y-%m-%d')
    ),
    dbc.Button("Download", id="download-data", n_clicks=0),
    dcc.Download(id="download-dataframe-xlsx1"),
    dcc.Loading(html.Div([
        dt.DataTable(
            id = 'substitute', 
            columns = [
                        {'name': 'Shift Date', 'id': 'Shift Date'},
                        {'name': 'Shift', 'id': 'Shift'},
                        {'name': 'Original Shift', 'id': 'Original Shift'},
                        {'name': 'Replacement', 'id': 'Replacement'},
                        {'name': 'Confirmed', 'id': 'Confirmed'},
                        {'name': 'Confirm Substitute', 'id': 'Confirm Substitute', 'presentation': 'markdown'},
                        {'name': 'Remarks', 'id': 'Remarks', 'editable':True},
                        {'name': 'Deny Substitute', 'id': 'Deny Substitute', 'presentation': 'markdown'}
                    ],
            style_cell_conditional=[
                {'if': {'column_id': 'Shift Date'}, 'width': '150px', 'textAlign': 'center'},
                {'if': {'column_id': 'Shift'}, 'width': '150px', 'textAlign': 'center'},
                {'if': {'column_id': 'Original Shift'}, 'width': '100px', 'textAlign': 'center'},
                {'if': {'column_id': 'Replacement'}, 'width': '150px', 'textAlign': 'center'},
                {'if': {'column_id': 'Confirmed'}, 'width': '150px', 'textAlign': 'center'},
                {'if': {'column_id': 'Remarks'}, 'width': '150px', 'textAlign': 'center'},
                {'if': {'column_id': 'Confirm Substitute'}, 'width': '150px', 'textAlign': 'center'},
                {'if': {'column_id': 'Deny Substitute'}, 'width': '150px', 'textAlign': 'center'}
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
    Output('substitute', 'data'),
    Input('data-store', 'data')
)
def update_table(data):
    return get_sub_data().to_dict("records")

# Define a callback to handle button clicks
@callback(
    [Output("notification", "is_open"),
     Output("notification", "children"),
     Output("notification", "color")],
    Output('data-store', 'data'),
    [Input('substitute', 'active_cell'),
    Input('substitute', 'data')],
    prevent_initial_call=False
)
def handle_button_click(active_cell,data):
    if active_cell is not None:
        print("active_cell detected")
        row_index = active_cell['row']
        row_data = data[row_index]
        column_id = active_cell['column_id']
        if column_id.startswith('Confirm Substitute'):
            confirm_substitute(row_data['Shift Date'].split("\n")[0],row_data['Original Shift'],row_data['Replacement'])
            temp_df = get_sub_data()
            return True,"Substitute confirmed!",'success',temp_df.to_dict("records")
        elif column_id.startswith('Deny Substitute'):
            if row_data.get('Remarks') is not None:
                remarks = row_data['Remarks']
                deny_substitute(row_data['Shift Date'].split("\n")[0],row_data['Shift'],row_data['Original Shift'],row_data['Replacement'],remarks,row_data['Confirmed'])
                temp_df = get_sub_data()
                return True,"Substitute Denied!",'success',temp_df.to_dict("records")
            else:
                print("remarks not given")
                temp_df = get_sub_data()
                return True,"Please Enter Remarks!",'danger',temp_df.to_dict("records")
    else:
        return False,'','info',get_sub_data().to_dict("records")
    raise dash.exceptions.PreventUpdate


# Callback function to update the style_data_conditional property
@callback(
    Output('substitute', 'style_data_conditional'),
    Input('substitute', 'data'),
    prevent_initial_call=True
)
def update_style_data_conditional(data):
    return [
        {
            'if': {'row_index': i},
            'backgroundColor': '#C6F4C5' if row['Confirmed'] == 'Yes' else '#FFFFC2',
            'color': 'black'
        } for i, row in enumerate(data)
    ]

def get_sub_data():
    sub_list = get_substitute_list()
    temp_list = {'Shift Date' : [], 'Shift':[], 'Original Shift' : [], 'Replacement' : [], 'Confirmed': [], }
    temp_list['Shift Date'].extend(sub_list['shift_date'])
    temp_list['Shift'].extend(sub_list['shift_type']) 
    temp_list['Original Shift'].extend(sub_list['orgn_shift'])
    temp_list['Replacement'].extend(sub_list['replacement'])
    temp_list['Confirmed'].extend(sub_list['is_confirmed'])
    temp_df = pd.DataFrame(temp_list)
    temp_df['Shift Date'] = pd.to_datetime(temp_df['Shift Date'])
    temp_df['Shift Date'] = temp_df['Shift Date'].dt.strftime('%d-%m-%Y') + "\n" + temp_df['Shift Date'].dt.strftime("%A")
    for i, row in temp_df.iterrows():
        temp_df.at[i, 'Confirm Substitute'] = f"[Confirm Substitute](#)"
        temp_df.at[i, 'Deny Substitute'] = f"[Deny Substitute](#)"

    return temp_df

# Callback to generate and download Excel file
@callback(
    Output("download-dataframe-xlsx1", "data"),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    Input("download-data", "n_clicks"),
    prevent_initial_call=True
)
def download_excel(start_date,end_date,n_clicks):

    data = get_sub_list(start_date,end_date)
    temp_df = pd.DataFrame(data)
    temp_df['shift_date'] = pd.to_datetime(temp_df['shift_date'])
    temp_df['shift_date'] = temp_df['shift_date'].dt.strftime('%d-%m-%Y') + "\n" + temp_df['shift_date'].dt.strftime("%A")
    final_df = pd.DataFrame({
        "Shift Date": temp_df["shift_date"],
        "Shift": temp_df["shift_type"],
        "Original Shift": temp_df["orgn_shift"],
        "Replacement": temp_df["replacement"],
        "Confirmed": temp_df["is_confirmed"]
    })
    final_df.index = final_df.index +1
    return dcc.send_data_frame(final_df.to_excel,"Substitute List.xlsx")