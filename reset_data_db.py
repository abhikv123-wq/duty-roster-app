# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 22:26:43 2025

@author: abhik
"""

import pandas as pd
import sqlite3
import numpy as np
import os

# ✅ Step 1: Define path to Excel and SQLite DB
excel_path = r"C:\Users\abhik\Duty Roster website\Shift_replacement_app - Copy\Shift_replacement_app - Copy\config\employee_data.xlsx"
db_path = r"C:\Users\abhik\Duty Roster website\Shift_replacement_app - Copy\Shift_replacement_app - Copy\data.db"

# ✅ Step 2: Load Excel data
data = pd.read_excel(excel_path)

# ✅ Step 3: Format datetime columns (if any)
for col in data.columns:
    if pd.api.types.is_datetime64_any_dtype(data[col]):
        data[col] = data[col].dt.strftime('%Y-%m-%d')

# ✅ Step 4: Clean and cast
data['employee_id'] = data['employee_id'].astype(str).str.strip().astype(int)
data = data.replace({np.nan: None})
data['is_active'] = data['is_active'].apply(lambda x: True if str(x).strip() == '1' else False)

# ✅ Step 5: Connect to SQLite
con = sqlite3.connect(db_path)
cur = con.cursor()

# ✅ Step 6: Optional - clear old data
cur.execute("DELETE FROM employee")

# ✅ Step 7: Insert data
query = """
    INSERT INTO employee (
        employee_id,
        name,
        designation,
        position,
        last_shift_attended,
        total_shift_attended,
        shift_replacement_denied,
        department,
        last_to_last_shift_attended,
        shift_group,
        is_active
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

data_list = [tuple(row) for row in data.values]
cur.executemany(query, data_list)
con.commit()

# ✅ Step 8: Close connection
cur.close()
con.close()

print("✅ Updated employee data inserted into SQLite successfully.")
