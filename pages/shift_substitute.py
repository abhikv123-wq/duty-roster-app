import dash
from dash import Dash, html, dcc, callback, Output, Input, State
from datetime import datetime, timedelta,date
import plotly.express as px
import dash_table as dt
import pandas as pd
from extract_data import employee_shift , employee_substitue, insert_substitute, get_substitute_list,get_leave_details,get_sub_list,get_employee_details,get_employee_update
from statistics import mean 
import os
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import calendar
import dash_dangerously_set_inner_html

dirname = os.path.dirname(__file__)
#filename = os.path.join(dirname, 'config\Data.xlsx')

dash.register_page(__name__,path='/shift_substitute')
#df = pd.read_excel(filename,sheet_name='shifts')

def serve_layout():
    return html.Div([
    html.H2(children='Shift Substitute', style={'textAlign':'center'}),
    dcc.DatePickerSingle(
        id='shift_date',
        min_date_allowed=datetime.today(),
        initial_visible_month=datetime.today(),
        display_format='DD-MM-YYYY',
        date= (datetime.today() + timedelta(1)).strftime("%Y-%m-%d"),
    ),
    html.Button("Get Shift Details", 
                id="roster",
                style={'fontSize': '18px', 
                    'fontWeight': 'bold', 
                    'color': '#ffffff', 
                    'backgroundColor': '#007bff', 
                    'borderRadius': '5px', 
                    'padding': '10px 20px',
                    'cursor': 'pointer'}),
    dcc.Loading(html.Div([
        dt.DataTable(
            id = 'shift', 
            columns = [
                        {'name': 'Date', 'id': 'Date','presentation': 'markdown'},
                        {'name': 'Evening Shift', 'id': 'Evening Shift','presentation': 'markdown'},
                        {'name': 'Morning Shift', 'id': 'Morning Shift','presentation': 'markdown'},
                        {'name': 'Night Shift', 'id': 'Night Shift','presentation': 'markdown'},
                        {'name': 'Weekly Off', 'id': 'Weekly Off','presentation': 'markdown'}
                    ],  
            style_cell={'whiteSpace': 'pre-wrap',
                        'textAlign': 'center'},
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
            markdown_options={'html': True}  # Allow HTML in markdown cells

        )   
    ]),type="default"),
    html.H3(children='Substitue for ', style={'textAlign':'center'}),
    dcc.Dropdown(
        id='shift-list',
        options=[
            {'label': 'Option 1', 'value': 'option1',}
        ],
        style={
                'fontSize': '18px'  # Increase font size to 16px
            }
    ),
    html.H3(children='Replacement ', style={'textAlign':'center'}),
    dcc.Dropdown(
        id='replacement',
        options=[
             {'label': 'Option 1', 'value': 'option1','presentation': 'markdown'}
        ],
        style={
                'fontSize': '18px'  # Increase font size to 16px
            }
    ),
    dbc.Button("Submit Substitute", 
                id="submit_substitute",
                style={'fontSize': '18px', 
                    'fontWeight': 'bold', 
                    'color': '#ffffff', 
                    'backgroundColor': '#007bff', 
                    'borderRadius': '5px', 
                    'padding': '10px 20px',
                    'cursor': 'pointer'}),
    dbc.Alert("This is a notification!", id="notification1", is_open=False, duration=5000,
              style={'position': 'fixed', 'top': '5px', 'right': '5px', 'width': '200px','fontWeight': 'bold'}),    
    dcc.Store(id="button-clicked", data=False)
])
layout = serve_layout

@callback(
    Output('shift','data'),
    Output('shift-list','options'),
    State('shift_date', 'date'),
    Input("roster", "n_clicks")
)
def update_table(start_date,n_clicks):

   
    employee_shift_data = employee_shift()
    emp_update_list = get_employee_update()
    #append leave detail in name
    leave_details = get_leave_details()
    substitute_list = get_substitute_list()

    temp_list = {'Date' : [],
                'Morning Shift':[],
                'Evening Shift' : [],
                'Night Shift' : [],
                'Weekly Off': [],
              }
    emp_on_leave = []

    temp = datetime.strptime(start_date,'%Y-%m-%d')

    # get group detail as per shift date 
    # Get Shift Employee Data
    filename = os.path.join(dirname, 'config\shift_roster.xlsx')
    df = pd.read_excel(filename)
    morning_shift = df[df['Date'] == temp]['Morning'].values[0]
    evening_shift = df[df['Date'] == temp]['Evening'].values[0]
    night_shift = df[df['Date'] == temp]['Night'].values[0]
    weekly_off = df[df['Date'] == temp]['Off'].values[0]

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
                    emp_on_leave.append(mor_list[i] + ', Morning Shift')
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
                    emp_on_leave.append(eve_list[i] + ', Evening Shift')
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
                    emp_on_leave.append(night_list[i] + ', Night Shift')
                    night_list[i] = '<span style="color: red;"> <del>' + night_list[i] + '</del></span>'

    temp_list['Date'].append(temp.strftime('%d-%m-%Y') + "\n" + temp.strftime("%A"))
    temp_list['Morning Shift'].append(mor_list)
    temp_list['Evening Shift'].append(eve_list)
    temp_list['Night Shift'].append(night_list)
    temp_list['Weekly Off'].append(off_list)

    temp_df = pd.DataFrame(temp_list)
    temp_df['Morning Shift'] = temp_df['Morning Shift'].apply(lambda x: '\n'.join(x))
    temp_df['Evening Shift'] = temp_df['Evening Shift'].apply(lambda x: '\n'.join(x))
    temp_df['Night Shift'] = temp_df['Night Shift'].apply(lambda x: '\n'.join(x))
    temp_df['Weekly Off'] = temp_df['Weekly Off'].apply(lambda x: '\n'.join(x))

    options_shift = [{'label': i, 'value': i} for i in emp_on_leave]

    return temp_df.to_dict("records"),options_shift

@callback(
    [Output("notification1", "is_open"),
     Output("notification1", "children"),
     Output("notification1", "color")],
    State('shift_date', 'date'),
    [State('shift-list', 'value')],
    [State('replacement', 'value')],
    Input("submit_substitute", "n_clicks"),
    prevent_initial_call=True
)   
def shift_substitute(shift_date,orgn_shift,replace,n_clicks):
        orgn_shift_emp = orgn_shift.split(",")[0].strip()
        shift_type = orgn_shift.split(",")[1].strip()
        # check if substitue is already assigend
        sub_list = get_substitute_list()
        sub_list['shift_date'] = pd.to_datetime(sub_list['shift_date'])
        if sub_list.loc[((sub_list['shift_date'].dt.date == datetime.strptime(shift_date,'%Y-%m-%d').date()) & 
                   (sub_list['orgn_shift'] == orgn_shift_emp)), 'is_confirmed'].eq('Yes').any():            
            return True,"Substitute already Assigned!", "danger"
        else:
            replace = replace.split(",")[0].strip()
            insert_substitute(orgn_shift_emp,replace,shift_date,shift_type,'No')
        return True,"Substitute added successfully!",'success'


@callback(
    Output('replacement', 'options'),
    Input('shift-list', 'value'),
    State('shift_date', 'date'),
    prevent_initial_call=True
)
def update_replacement(value,date):
    input_date = datetime.strptime(date,'%Y-%m-%d')
    start_date = input_date.replace(day=1).strftime('%Y-%m-%d')
    end_date = datetime(input_date.year, input_date.month, calendar.monthrange(input_date.year, input_date.month)[1]).strftime('%Y-%m-%d')
    temp_sub_list = get_sub_list(start_date,end_date)
    replacement_list = []
    replacement_list.extend(temp_sub_list['replacement'])
    employee_substitute_data = employee_substitue()
    emp_details = get_employee_details(value.split(',')[0])
    if value is not None:
        if emp_details['position'][0]=='1':
            sub_list = employee_substitute_data[employee_substitute_data['position'] == '1'].apply(lambda row: ','.join([row['name'], row['designation'], row['department']]), axis=1).tolist() 
            options_rep = []
            for i in range(len(sub_list)):
                if sub_list[i].split(',')[0] in replacement_list:
                    options_rep.append({'label': dash_dangerously_set_inner_html.DangerouslySetInnerHTML("'<b>"+ sub_list[i] + "</b>'"), 'value': sub_list[i] })
                else:
                    options_rep.append({'label': sub_list[i], 'value': sub_list[i]})
        else:
            sub_list = employee_substitute_data[employee_substitute_data['position'] != '1'].apply(lambda row: ','.join([row['name'], row['designation'], row['department']]), axis=1).tolist()            
            options_rep = []
            for i in range(len(sub_list)):
                if sub_list[i].split(',')[0] in replacement_list:
                    options_rep.append({'label': dash_dangerously_set_inner_html.DangerouslySetInnerHTML("'<b>"+ sub_list[i] + "</b>'"), 'value': sub_list[i] })
                else:
                    options_rep.append({'label': sub_list[i], 'value': sub_list[i]})
        return options_rep
    else:
        options =[
            {'label': 'Option 1', 'value': 'option1'}
        ]
        return options
