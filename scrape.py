import os
import pymssql
import pymupdf
import pandas as pd

# Establish SQL database connection
try:
    db = pymssql.connect(
        server='{REDACTED}',
        user='{REDACTED}',
        password='{REDACTED}',
        database='{REDACTED}',
        port='{REDACTED}'
    )
    cursor = db.cursor()
except pymssql.Error as err:
    print("Login credentials invalid" + err)

# Getting destination sub folder
root = "C:\\Test"

# Initialize categories
classes = ['Case Title', 'Department', 'Case Number',
                  'Judge', 'Hearing Type', 'Hearing Date',
                  'Clerk', 'Court Reporter', 'Interpreter',
                  'Court Officer']

new_classes = []

child_columns = ("ID, Count, Statute, OffenseType, "
                 "PreparatoryOffense, Degree, Plea, "
                 "Disposition")

columns = ("CaseTitle, Department, CaseNumber, Judge, "
           "HearingType, HearingDate, Clerk, CourtReporter, "
           "Interpreter, CourtOfficer")

"""
Modify
Usage: PDF OCR scan has been completed
Output: Raw text data from PDF
"""
def ocr_ready(path, file):
    with pymupdf.open(path) as pdf:
        text = chr(12).join(i.get_text() for i in pdf)
        page = pdf[0]
        if not text.isspace():
            try:
                tables = page.find_tables()
                t0_data = tables[0].extract()
                if '' in t0_data[3]:
                    t0_data.remove(t0_data[3])
                main_classify(t0_data, path)
                if tables[1]:
                    t1_data = tables[1].extract()
                    child_classify(t1_data, file)
            except IndexError:
                print("Error: No table found")
                return

"""
Usage: Classify data from main table and store in SQL
"""
def main_classify(table, path):
    list = []
    for block in table:
        if block[0] and block[2] in classes:
            list.append(block[1])
            list.append(block[3])
    # print(list)
    try:
        sql_query = ("insert into dbo.cri ({}) \
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(columns))
        cursor.execute(sql_query, tuple(list))
        db.commit()
    except pymssql.DatabaseError:
        print("Error: Could not send request to SQL database.")
        return

"""
Usage: Classify data from second table (if it exists) and store in SQL
"""
def child_classify(table, file):
    file = file.split("_")[0]
    try:
        for i in range(1, len(table)):
            list = [file]
            for j in range(0, len(table[0])):
                list.append(table[i][j])
            # print(list)
            sql_query = ("insert into dbo.counts ({}) \
                             values (%s,%s,%s,%s,%s,%s,%s,%s)".format(child_columns))
            cursor.execute(sql_query, tuple(list))
            db.commit()
    except IndexError:
        print("Error: Incorrectly formatted table")
        return
    except pymssql.DatabaseError:
        print("Error: Could not send request to SQL database.")
        return


"""
Usage: Iterate through CourtMinutes
Output: None
"""
def run():
    min_path = root + "\\CourtMinutes"
    for folder in os.listdir(min_path):
        path = min_path + '\\' + folder
        for file in os.listdir(path):
            if file.endswith('.pdf') or file.endswith('.docx'):
                # print('File:', file)
                ocr_ready(path + '\\' + file, file)

run()
# print(columns)
cursor.close()
db.close()