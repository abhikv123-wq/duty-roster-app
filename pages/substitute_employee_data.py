import calendar
import dash
from dash import Dash, html, dcc, callback, Output, Input, State
from datetime import datetime, timedelta,date
import plotly.express as px
import dash_table as dt
import pandas as pd
from extract_data import get_substitute_employee,get_shift_denied, get_sub_list
import os
from dash.exceptions import PreventUpdate
from dash import callback_context
import dash_bootstrap_components as dbc
from io import BytesIO
from xlsxwriter import Workbook

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'config\Data.xlsx')

dash.register_page(__name__,path='/substitute_employee_data')

def serve_layout():
    return html.Div([
    dcc.Store(id='table-data-1', data=None),
    html.H2(children='Substitute Employees Data', style={'textAlign':'center'}),
    dcc.DatePickerRange(
        id='date-range',
        initial_visible_month= datetime.today(),
        display_format='DD-MM-YYYY',
        start_date= datetime(datetime.today().year, datetime.today().month, 1).strftime('%Y-%m-%d'),
        end_date=datetime(datetime.today().year, datetime.today().month, calendar.monthrange(datetime.today().year, datetime.today().month)[1]).strftime('%Y-%m-%d'),
        style={'zIndex': '9999', 'position': 'relative'}
    ),
    html.Button("Submit", 
                id="fetch_data",
                style={'fontSize': '18px', 
                    'fontWeight': 'bold', 
                    'color': '#ffffff', 
                    'backgroundColor': '#007bff', 
                    'borderRadius': '5px', 
                    'padding': '10px 20px',
                    'cursor': 'pointer'}),
    html.Button("Download", 
                id="download-data1",
                style={'fontSize': '18px', 
                    'fontWeight': 'bold', 
                    'color': '#ffffff', 
                    'backgroundColor': '#007bff', 
                    'borderRadius': '5px', 
                    'padding': '10px 20px',
                    'cursor': 'pointer'}),
    dcc.Download(id="download-dataframe-xlsx"),
    dcc.Loading(html.Div([
        dt.DataTable(
            id = 'emp_data', 
            columns = [
                        {'name': 'Name', 'id': 'Name'},
                        {'name': 'Designation', 'id': 'Designation'},
                        {'name': 'Position', 'id': 'Position','sortable': True},
                        {'name': 'Last Shift Attended', 'id': 'Last Shift Attended','sortable': True},
                        {'name': 'Total Shift Attended', 'id': 'Total Shift Attended'},
                        {'name': 'Total Shfit Replacement Denied', 'id': 'Total Shfit Replacement Denied'},
                        {'name': 'Shift Duty Denied Dates and Reason', 'id': 'Shift Duty Denied Dates and Reason'},
                    ],
            style_cell={'whiteSpace': 'pre-wrap'},
            style_cell_conditional=[
                {'if': {'column_id': 'Name'}, 'width': '100px', 'textAlign': 'center'},
                {'if': {'column_id': 'Designation'}, 'width': '50px', 'textAlign': 'center'},
                {'if': {'column_id': 'Position'}, 'width': '50px', 'textAlign': 'center'},
                {'if': {'column_id': 'Last Shift Attended'}, 'width': '10px', 'textAlign': 'center'},
                {'if': {'column_id': 'Total Shift Attended'}, 'width': '50px', 'textAlign': 'center'},
                {'if': {'column_id': 'Total Shfit Replacement Denied'}, 'width': '100px', 'textAlign': 'center'},
                {'if': {'column_id': 'Shift Duty Denied Dates and Reason'}, 'width': '300px', 'textAlign': 'center'}

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
            style_table={'overflowY': 'scroll', 'height': '3000px'},
            fixed_rows={'headers': True},
            sort_action='native',  # Enable sorting by clicking column headers
        )
    ]),type="default"),
])
layout = serve_layout

@callback(
    Output('emp_data', 'data'),
    Output('table-data-1','data'),
    Input("fetch_data", "n_clicks"),
    State('table-data-1', 'data'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
)
def update_table_data(n_clicks, table_data, start_date, end_date):
    data = get_substitute_employee()
    subs = get_sub_list(start_date, end_date)
    duty_denied = get_shift_denied(start_date, end_date)

    temp_list = {
        'Name': [],
        'Designation': [],
        'Position': [],
        'Last Shift Attended': [],
        'Total Shift Attended': [],
        'Total Shfit Replacement Denied': [],
        'Shift Duty Denied Dates and Reason': [],
    }

    temp_list['Name'].extend(data['name'])
    temp_list['Designation'].extend(data['designation'])
    temp_list['Position'].extend(data['position'])

    # Make sure 'shift_date' is a datetime object
    subs['shift_date'] = pd.to_datetime(subs['shift_date'])
    # Group by name and get the latest shift_date
    latest_shift_map = subs.groupby('replacement')['shift_date'].max().dt.strftime('%d-%m-%Y').to_dict()
    data['last_shift_attended'] = data['name'].map(latest_shift_map).fillna('')
    temp_list['Last Shift Attended'].extend(data['last_shift_attended'])

    # Count shifts attended
    name_counts = subs['replacement'].value_counts()
    data['subs_count'] = data['name'].map(name_counts).fillna(0).astype(int)
    temp_list['Total Shift Attended'].extend(data['subs_count'])

    # Count denied shifts
    name_counts = duty_denied['name'].value_counts()
    data['denied_count'] = data['name'].map(name_counts).fillna(0).astype(int)
    temp_list['Total Shfit Replacement Denied'].extend(data['denied_count'])

    # Build reason map: (shift_date, shift_type) -> remark
    def build_shift_map(group):
        return {
            (row['shift_date'], row['shift_type']): row['remarks']
            for _, row in group.iterrows()
        }

    name_shift_map = duty_denied.groupby('name').apply(build_shift_map).to_dict()

    # Format the shift map (dictionary) into a readable string
    def format_reason_map(shift_map):
        if not isinstance(shift_map, dict) or not shift_map:
            return ''
        return '\n'.join([f"{date} ({stype}): {remark}" for (date, stype), remark in shift_map.items()])

    # Use the formatter after mapping
    data['shift_denied_reason'] = data['name'].map(name_shift_map).apply(format_reason_map).fillna('')

    # Then extend the list with clean strings
    temp_list['Shift Duty Denied Dates and Reason'].extend(data['shift_denied_reason'].astype(str))

    temp_df = pd.DataFrame(temp_list)

    return temp_df.to_dict("records"), temp_df.to_dict("records")

# Callback function to update the style_data_conditional property
@callback(
    Output('emp_data', 'style_data_conditional'),
    Input('emp_data', 'data'),
    prevent_initial_call=True
)
def update_style_data_conditional(data):
    return [{
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f9f9f9'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': '#ffffff'
        }],[{
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f9f9f9'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': '#ffffff'
        }]
    
    
# Callback to generate and download Excel file
@callback(
    Output("download-dataframe-xlsx", "data"),
    State('table-data-1', 'data'),
    Input("download-data1", "n_clicks"),
    prevent_initial_call=True
)
def download_excel(data,n_clicks):

    first_df = pd.DataFrame(data)
    output = os.path.join(dirname, 'output.xlsx')
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write the first DataFrame to the first sheet
        first_df.to_excel(writer, sheet_name="Substitute Employee", index=False)
        # Write the second DataFrame to the second sheet    
    # Return the Excel file for download
    return dcc.send_file(output, "Substitute Employee Data.xlsx")