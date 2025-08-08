import calendar
import dash
from html import unescape
from dash import Dash, html, dcc, callback, Output, Input, State
from datetime import datetime, timedelta,date
import numpy as np
import plotly.express as px
import dash_table as dt
import pandas as pd
from extract_data import employee_shift , get_leave_details, get_sub_list,get_employee_update,get_employee_details
from statistics import mean 
import os
import dash_table
import dash_bootstrap_components as dbc
import re
from dash import clientside_callback  # Ensure this is imported properly
from html import unescape

dash.register_page(__name__,path='/')

import os

# Get absolute path relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(BASE_DIR, "config", "shift_roster.xlsx")




def serve_layout():
    return html.Div([
    html.H2(children='Shift Roster', style={'textAlign':'center'}),

    dcc.DatePickerRange(
        id='my-date-picker-range',
        initial_visible_month= datetime.today(),
        display_format='DD-MM-YYYY',
        start_date= datetime(datetime.today().year, datetime.today().month, 1).strftime('%Y-%m-%d'),
        end_date=datetime(datetime.today().year, datetime.today().month, calendar.monthrange(datetime.today().year, datetime.today().month)[1]).strftime('%Y-%m-%d')
    ),
    html.Button("Submit", 
                id="roster",
                style={'fontSize': '18px', 
                    'fontWeight': 'bold', 
                    'color': '#ffffff', 
                    'backgroundColor': '#007bff', 
                    'borderRadius': '5px', 
                    'padding': '10px 20px',
                    'cursor': 'pointer'}),
    html.Button("Download Night Shift Statistics", 
                id="night-shift-data",
                style={'fontSize': '18px', 
                    'fontWeight': 'bold', 
                    'color': '#ffffff', 
                    'backgroundColor': '#007bff', 
                    'borderRadius': '5px', 
                    'padding': '10px 20px',
                    'cursor': 'pointer'}),
    dcc.Download(id="download-night-stats"),
    html.Button("Download Shift Roster", 
                id="shift-roster-btn",
                style={'fontSize': '18px', 
                    'fontWeight': 'bold', 
                    'color': '#ffffff', 
                    'backgroundColor': '#007bff', 
                    'borderRadius': '5px', 
                    'padding': '10px 20px',
                    'cursor': 'pointer'}),
    dcc.Download(id="download-shift-roster"),
    dcc.Loading(html.Div([
        dt.DataTable(
            id = 'shift_roster', 
            columns = [
                        {'name': 'Date', 'id': 'Date','presentation': 'markdown'},
                        {'name': 'Evening Shift', 'id': 'Evening Shift','presentation': 'markdown'},
                        {'name': 'Morning Shift', 'id': 'Morning Shift','presentation': 'markdown'},
                        {'name': 'Night Shift', 'id': 'Night Shift','presentation': 'markdown'},
                        {'name': 'Weekly Off', 'id': 'Weekly Off','presentation': 'markdown'}
                    ],            
            style_cell={'whiteSpace': 'pre-wrap'},
            style_cell_conditional=[
                {'if': {'column_id': 'Date'}, 'width': '100px', 'textAlign': 'center'},
                {'if': {'column_id': 'Evening Shift'}, 'width': '300px', 'textAlign': 'center'},
                {'if': {'column_id': 'Morning Shift'}, 'width': '300px', 'textAlign': 'center'},
                {'if': {'column_id': 'Night Shift'}, 'width': '300px', 'textAlign': 'center'},
                {'if': {'column_id': 'Weekly Off'}, 'width': '150px', 'textAlign': 'center'},
            ],
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
            style_table={'overflowY': 'scroll', 'height': '2400px'},
            fixed_rows={'headers': True},
            markdown_options={'html': True}  # Allow html in markdown cells
        )   
    ]),type="default")
  
])
layout = serve_layout

@callback(
    Output('shift_roster','data'),
    State('my-date-picker-range', 'start_date'),
    State('my-date-picker-range', 'end_date'),
    Input("roster", "n_clicks"),
)
def update_roster(start_date,end_date,n_clicks):

    # Get update about employee shifting to different groups or in general
    emp_update_list = get_employee_update()
    leave_details = get_leave_details()
    substitute_list = get_sub_list(start_date,end_date)
    temp_list = {'Date' : [],
                'Morning Shift':[],
                'Evening Shift' : [],
                'Night Shift' : [],
                'Weekly Off': []
              }
    total_days = datetime.strptime(end_date,'%Y-%m-%d') - datetime.strptime(start_date,'%Y-%m-%d')
    for i in range(0,total_days.days+1):
        temp = datetime.strptime(start_date,'%Y-%m-%d') + timedelta(i)

        # get group detail as per shift date
        # Get Shift Employee Data
        filename = os.path.join(BASE_DIR, "config", "shift_roster.xlsx")
        df = pd.read_excel(filename)
        morning_shift = df[df['Date'] == temp]['Morning'].values[0]
        evening_shift = df[df['Date'] == temp]['Evening'].values[0]
        night_shift = df[df['Date'] == temp]['Night'].values[0]
        weekly_off = df[df['Date'] == temp]['Off'].values[0]

        employee_shift_data = employee_shift()
        # Update employee_Shift_data
        emp_update_list['date'] = pd.to_datetime(emp_update_list['date'])
        emp_update_temp = emp_update_list[temp < emp_update_list['date']]
        emp_update_temp = emp_update_temp.drop_duplicates(subset='name', keep='first')
        
        for col in employee_shift_data.columns:
            if col not in emp_update_temp.columns:
                emp_update_temp[col] = ''
        emp_update_temp.loc[:, 'shift_group'] = emp_update_temp['duty_old']
        emp_update_temp = emp_update_temp.drop('duty_old', axis=1)
        emp_update_temp.reset_index(inplace=True)
        if not emp_update_temp.empty:
            if emp_update_temp['name'][0] in employee_shift_data['name'].values:
                employee_shift_data.loc[employee_shift_data['name'] == emp_update_temp['name'][0], 'shift_group'] = emp_update_temp['shift_group'][0]
            else:
                employee_shift_data = pd.concat([employee_shift_data, emp_update_temp[employee_shift_data.columns]], ignore_index=True)
        else:
            employee_shift_data = pd.concat([employee_shift_data, emp_update_temp[employee_shift_data.columns]], ignore_index=True)
        employee_shift_data = employee_shift_data.drop_duplicates(subset=['name', 'shift_group'], keep='first')


        mor_list = employee_shift_data[employee_shift_data['shift_group']== morning_shift].name.tolist()
        eve_list = employee_shift_data[employee_shift_data['shift_group']== evening_shift].name.tolist()
        night_list = employee_shift_data[employee_shift_data['shift_group']== night_shift].name.tolist()
        off_list = employee_shift_data[employee_shift_data['shift_group']== weekly_off].name.tolist()

        #append leave detail in name
        leave_details['date'] = pd.to_datetime(leave_details['date'])
        substitute_list['shift_date'] = pd.to_datetime(substitute_list['shift_date'])

        leave_list = leave_details[leave_details['date'] == temp]['emp_name'].values.tolist()

        for i, element in enumerate(mor_list):
            sub_assgn_conf = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'Yes') & (substitute_list['shift_type'] == 'Morning Shift')]['orgn_shift'].values.tolist()
            sub_assgn = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'No') & (substitute_list['shift_type'] == 'Morning Shift')]['orgn_shift'].values.tolist()
            sub_df = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'Yes') & (substitute_list['shift_type'] == 'Morning Shift')]
            if element in leave_list:
                if element in sub_assgn_conf:
                    tmp = mor_list[i]
                    mor_list[i] = '<span style="color: red;"> <del>' + mor_list[i] + '</del></span>'
                    mor_list[i] += " (" + sub_df[sub_df['orgn_shift'] == tmp]['replacement'].values[0] + ")"
                elif element in sub_assgn:
                    tmp = mor_list[i]
                    mor_list[i] = '<span style="color: red;"> <del>' + mor_list[i] + '</del></span>'
                    mor_list[i] += "(Not Confirmed)"
                else:
                    mor_list[i] = '<span style="color: red;"> <del>' + mor_list[i] + '</del></span>'

        for i, element in enumerate(eve_list):
            sub_assgn_conf = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'Yes') & (substitute_list['shift_type'] == 'Evening Shift')]['orgn_shift'].values.tolist()
            sub_assgn = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'No') & (substitute_list['shift_type'] == 'Evening Shift')]['orgn_shift'].values.tolist()
            sub_df = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'Yes') & (substitute_list['shift_type'] == 'Evening Shift')]
            if element in leave_list:
                if element in sub_assgn_conf:
                    tmp = eve_list[i]
                    eve_list[i] = '<span style="color: red;"> <del>' + eve_list[i] + '</del></span>'
                    eve_list[i] += " (" + sub_df[sub_df['orgn_shift'] == tmp]['replacement'].values[0] + ")"
                elif element in sub_assgn:
                    eve_list[i] = '<span style="color: red;"> <del>' + eve_list[i] + '</del></span>'
                    eve_list[i] += "(Not Confirmed)"
                else:
                    eve_list[i] = '<span style="color: red;"> <del>' + eve_list[i] + '</del></span>'
        for i, element in enumerate(night_list):
            sub_assgn_conf = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'Yes') & (substitute_list['shift_type'] == 'Night Shift')]['orgn_shift'].values.tolist()
            sub_assgn = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'No') & (substitute_list['shift_type'] == 'Night Shift')]['orgn_shift'].values.tolist()
            sub_df = substitute_list[(substitute_list['shift_date'] == temp) & (substitute_list['is_confirmed'] == 'Yes') & (substitute_list['shift_type'] == 'Night Shift')]
            if element in leave_list:
                if element in sub_assgn_conf:
                    tmp = night_list[i]
                    night_list[i] = '<span style="color: red;"> <del>' + night_list[i] + '</del></span>'
                    night_list[i] += " (" + sub_df[sub_df['orgn_shift'] == tmp]['replacement'].values[0] + ")"
                elif element in sub_assgn:
                    night_list[i] = '<span style="color: red;"> <del>' + night_list[i] + '</del></span>'
                    night_list[i] += "(Not Confirmed)"
                else:
                    night_list[i] = '<span style="color: red;"> <del>' + night_list[i] + '</del></span>'
        temp_list['Date'].append(temp.strftime('%d-%m-%Y') + "<br>" + temp.strftime("%A"))
        temp_list['Morning Shift'].append(mor_list)
        temp_list['Evening Shift'].append(eve_list)
        temp_list['Night Shift'].append(night_list)
        temp_list['Weekly Off'].append(off_list)

    temp_df = pd.DataFrame(temp_list)
    temp_df['Morning Shift'] = temp_df['Morning Shift'].apply(lambda x: '<br>'.join(x))
    temp_df['Evening Shift'] = temp_df['Evening Shift'].apply(lambda x: '<br>'.join(x))
    temp_df['Night Shift'] = temp_df['Night Shift'].apply(lambda x: '<br>'.join(x))
    temp_df['Weekly Off'] = temp_df['Weekly Off'].apply(lambda x: '<br>'.join(x))
    records = temp_df.to_dict("records")
    return records
# Callback function to update the style_data_conditional property
@callback(
    Output('shift_roster', 'style_data_conditional'),
    Input('shift_roster', 'data'),
    prevent_initial_call=True
)
def update_style_data_conditional(data):
    return [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f9f9f9'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': '#ffffff'
        }
    ]
# Callback to generate and download Excel file
@callback(
    Output("download-night-stats", "data"),
    State('shift_roster', 'data'),
    Input("night-shift-data", "n_clicks"),
    State('my-date-picker-range', 'start_date'),
    State('my-date-picker-range', 'end_date'),
    prevent_initial_call=True
)
def download_excel(data,n_clicks,start_date,end_date):

    temp_df = pd.DataFrame(data)
    night_list = temp_df[["Date","Night Shift"]]
    night_list['Date'] = night_list['Date'].str.extract(r'(\d{2}-\d{2}-\d{4})')
    night_list['Date'] = pd.to_datetime(night_list['Date'],dayfirst=True)
    night_list['Date'] = night_list['Date'].dt.day
    # Create a new list where each element is a line
    new_list = []
    for i, text in enumerate(night_list["Night Shift"]):
        # Split the text into lines
        lines = text.split('<br>')
        # Add each line with the corresponding date
        for line in lines:
            if "<span" in line:
                matches = re.findall(r'\((.*?)\)', line)
                try:
                    first_element = matches[0]
                except IndexError:
                    first_element = ''
                new_list.append([night_list["Date"][i], first_element])
            else:
                new_list.append([night_list["Date"][i], line])

    # Convert the new list to a DataFrame
    final_df = pd.DataFrame(new_list, columns=['Date', 'Night Shift'])
    result_df = final_df.groupby('Night Shift')['Date'].agg(list).reset_index()
    result_df.rename(columns={'Night Shift': 'Employee Name'}, inplace=True)
    result_df.rename(columns={'Date': 'Night Shift Attended on'}, inplace=True)
    
    result_df.set_index("Employee Name",inplace=True)

    return dcc.send_data_frame(result_df.to_excel,"Night Shift Statistics-" + start_date + " to " + end_date + ".xlsx")

@callback(
    Output('download-shift-roster', 'data'),
    State('shift_roster', 'data'),
    State('my-date-picker-range', 'start_date'),
    State('my-date-picker-range', 'end_date'),
    Input('shift-roster-btn', 'n_clicks'),
    prevent_initial_call=True
)
def generate_html(data, start_date, end_date, n_clicks):
    if n_clicks > 0:
        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        # Convert the DataFrame to HTML with custom row styling
        table_html = df.to_html(classes='table table-striped', index=False)

        # Decode the HTML entities
        table_html = unescape(table_html)

        # Add inline CSS for row coloring and borders
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .table {{
                        width: 100%;
                        border-collapse: collapse;
                        border: 1px solid #ddd;  /* Add border to the table */
                    }}
                    .table th, .table td {{
                        padding: 8px;
                        text-align: left;
                        border: 1px solid #ddd;  /* Add border to table cells */
                    }}
                    .table th {{
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }}
                    .odd-row {{ background-color: #f9f9f9; }}  /* Odd rows */
                    .even-row {{ background-color: #ffffff; }} /* Even rows */
                </style>
            </head>
            <body>
                <h1>Shift Roster</h1>
                <table class="table table-striped">
                    <thead>
                        {table_html.split('<thead>')[1].split('</thead>')[0]}
                    </thead>
                    <tbody>
        """

        # Manually insert row styles for odd/even rows
        for idx, row in df.iterrows():
            row_html = f'<tr class="{"odd-row" if idx % 2 == 0 else "even-row"}">'
            for col in df.columns:
                row_html += f"<td>{row[col]}</td>"
            row_html += '</tr>'
            html_content += row_html

        # Close the HTML content structure
        html_content += """
                    </tbody>
                </table>
            </body>
        </html>
        """

        # Save the html content as a file
        output_dir = os.path.join(os.getcwd(), 'temp')  # Adjust path if necessary
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "Shift_Roster_" + start_date + "-" + end_date + ".html")
        with open(output_file, "w") as f:
            f.write(html_content)

        # Return the file as a downloadable item
        result = dcc.send_file(output_file)

        # Delete the file after it has been downloaded
        os.remove(output_file)

        return result
