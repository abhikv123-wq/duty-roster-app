import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta
import psycopg2
import os
import sqlite3

dirname = os.getcwd()
db_file_path = os.path.join(dirname, 'data.db')

#db_file_path = os.path.join("K:\Sanjay\python_projects\Shift_replacement_app", 'data.db')


def employee_shift():
    print(db_file_path)
    con = sqlite3.connect(db_file_path)

    sql_query = pd.read_sql_query("select * from employee where shift_group != 'General' and is_active != False order by position",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    
    return data


def employee_substitue():
    con = sqlite3.connect(db_file_path)


    sql_query = pd.read_sql_query("select * from employee where shift_group = 'General' and is_active != False order by last_shift_attended asc ",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    
    return data

def insert_substitute(orgn_shift,replace,shift_date,shift_type,isconfirmed):
    con = sqlite3.connect(db_file_path)

    
    query = """
        INSERT OR REPLACE INTO substitute_list 
        (timestamp, orgn_shift, replacement, shift_date, shift_type, is_confirmed) 
        VALUES (?, ?, ?, ?, ?, ?)
        """

    params = (datetime.today(), orgn_shift, replace, shift_date, shift_type, isconfirmed)

    con.execute(query, params)
    con.commit()

def get_substitute_list():
    con = sqlite3.connect(db_file_path)


    sql_query = pd.read_sql_query("select * from substitute_list where shift_date > '" + datetime.today().date().strftime('%Y-%m-%d') + "' order by shift_date asc",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    
    return data


def confirm_substitute(shift_date,orgn_shift,replacement):
    con = sqlite3.connect(db_file_path)
    shift_date = datetime.strptime(shift_date,'%d-%m-%Y')
    shift_date = shift_date.strftime('%Y-%m-%d')

    con.execute("UPDATE substitute_list SET is_confirmed = 'Yes' WHERE shift_date = '" + shift_date + "' AND orgn_shift = '" + orgn_shift + "'")
    con.execute("UPDATE employee SET total_shift_attended = total_shift_attended + 1 where name = '" + replacement + "'")
    con.execute("UPDATE employee SET last_to_last_shift_attended = last_shift_attended where name = '" + replacement + "'")
    con.execute("UPDATE employee SET last_shift_attended = '" + shift_date + "' where name = '" + replacement + "'")


    con.commit()
    con.close()

def deny_substitute(shift_date,shift_type,orgn_shift,replacement,remarks,confirmed):
    con = sqlite3.connect(db_file_path)
    shift_date = datetime.strptime(shift_date,'%d-%m-%Y')
    shift_date = shift_date.strftime('%Y-%m-%d')
    con.execute("DELETE FROM substitute_list WHERE shift_date = '" + shift_date + "' AND orgn_shift = '" + orgn_shift + "'")
    con.execute("UPDATE employee SET shift_replacement_denied = shift_replacement_denied + 1 where name = '" + replacement + "'")
    query = """INSERT INTO shift_denied (timestamp,name,shift_date,shift_type, remarks) VALUES (?,?,?,?,?)"""
    params = (datetime.today(),replacement,shift_date,shift_type,remarks)
    con.execute(query, params)

    if confirmed =='Yes':
        con.execute("UPDATE employee SET total_shift_attended = total_shift_attended - 1 where name = '" + replacement + "'")
        con.execute("UPDATE employee SET last_shift_attended = last_to_last_shift_attended  where name = '" + replacement + "'")


    con.commit()
    con.close()

def insert_leave_details(date,emp_name):

    con = sqlite3.connect(db_file_path)
    query = """INSERT OR REPLACE INTO leave_details (date,emp_name) VALUES (?,?)"""

    params = (date,emp_name)
    con.execute(query, params)
    con.commit()
    con.close()

def get_leave_details():
    con = sqlite3.connect(db_file_path)
    sql_query = pd.read_sql_query("select date, emp_name from leave_details order by date asc",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    return data

def get_substitute_employee():
    con = sqlite3.connect(db_file_path)
    sql_query = pd.read_sql_query("select * from employee where shift_group = 'General' ",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    return data
def get_shift_denied(start_date,end_date):
    con = sqlite3.connect(db_file_path)
    sql_query = pd.read_sql_query("select * from shift_denied where shift_date >='" + start_date + "' and shift_date <= '" + end_date + "'",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    return data
def get_sub_list(start_date,end_date):
    con = sqlite3.connect(db_file_path)
    sql_query = pd.read_sql_query("select * from substitute_list where shift_date >='" + start_date + "' and shift_date <= '" + end_date + "' order by shift_date asc",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    
    return data

def delete_leave(emp_name, date):
    con = sqlite3.connect(db_file_path)
    print(emp_name)
    print(date)
    con.execute("DELETE FROM leave_details where date = '" + date + "' and emp_name = '" + emp_name + "'")
    con.commit()
    con.close()


def insert_employee(emp_id, name, designation, position, department, duty_type,is_active):
    con = sqlite3.connect(db_file_path)
    print("inside insert_employee")
    query = """INSERT INTO employee (employee_id, name, designation, position, last_shift_attended, total_shift_attended, shift_replacement_denied, department, last_to_last_shift_attended,shift_group,is_active) VALUES (?,?,?,?,?,?,?,?,?,?,?)"""
    params = (emp_id,name,designation,position,"1990-01-01",0,0,department,"1990-01-01",duty_type,is_active)
    con.execute(query, params)
    con.commit()
    con.close()

def update_employee(emp_id, name, designation, position, department, duty_type,is_active):
    con = sqlite3.connect(db_file_path)
    print("inside Update_employee")
    query = """
        UPDATE employee 
        SET designation = ?, 
            position = ?, 
            department = ?, 
            shift_group = ?, 
            is_active = ? 
        WHERE name = ?
    """

    params = (designation, position, department, duty_type, is_active, name)

    con.execute(query, params)
    con.commit()  # Save the changes    con.commit()
    con.close()

def delete_employee(name):
    con = sqlite3.connect(db_file_path)
    print("inside delete_employee")
    con.execute("UPDATE employee SET is_active = 0 where name = '" + name + "'")
    con.commit()
    con.close()

def get_emp():
    con = sqlite3.connect(db_file_path)
    sql_query = pd.read_sql_query("select name from employee ",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    return data


def get_employee_details(emp_name):
    con = sqlite3.connect(db_file_path)
    sql_query = pd.read_sql_query("select * from employee where name = '" + emp_name +"'",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    return data

def update_employee_status(date, emp_name,duty_old, duty_new):
    con = sqlite3.connect(db_file_path)
    query = """
    INSERT INTO employee_update (date, name, duty_old, duty_new)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(date, name) DO UPDATE SET
        duty_old = excluded.duty_old,
        duty_new = excluded.duty_new;    
    """
    params = (date,emp_name,duty_old,duty_new)
    con.execute(query, params)
    con.commit()
    con.close()

def get_employee_update():
    con = sqlite3.connect(db_file_path)
    sql_query = pd.read_sql_query("select * from employee_update order by date asc",con)
    data =  pd.DataFrame(sql_query)
    con.close()
    return data