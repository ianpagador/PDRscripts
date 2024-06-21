import pymssql
import pymupdf
import logging
import re
import pandas as pd
import time

start = time.time()

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
    logging.info("Login credentials invalid" + err)

# Getting destination sub folder
root = "C:\\Test"

logger = logging.getLogger(__name__)
logging.basicConfig(filename='scrape.log', level=logging.INFO, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info("scrape.py started.")

# Initialize categories

# This is a list that stores all the pd_minute_orders table's current columns
body_columns = []

# This is a list that initially stores all of Table 1's classes, but grows when more are found in
# the document
main_classes = ['Case Title', 'Department', 'Case Number',
                'Judge', 'Hearing Type', 'Hearing Date',
                'Clerk', 'Court Reporter', 'Interpreter',
                'Court Officer']

# This is a list that initializes
body_content = []

columns_str = ("CaseTitle, Department, CaseNumber, Judge, "
               "HearingType, HearingDate, Clerk, CourtReporter, "
               "Interpreter, CourtOfficer")

t2_columns_str = ("ID, Count, Statute, OffenseType, "
                  "PreparatoryOffense, Degree, Plea, "
                  "Disposition")

"""def make_table(name, columns, size):
    global body_columns
    table_name = 'pd_' + name
    column_list = columns.split(', ')
    init_list = []
    for i in range(0, len(column_list)):
        column_list[i] += ' varchar(MAX)'
    final_str = ', '.join(column_list)
    final_query = ("create table dbo.{} ({});".format(table_name, final_str, table_name))
    cursor.execute(final_query)"""

"""
Usage: Classify data from main table and store in SQL
Output: List of value entries
"""


def main_classify(table):
    index = 0
    for block in table:
        if block[0] and block[2] in main_classes:
            body_content[index] += block[1]
            body_content[index + 1] += block[3]
            index += 2


"""
Usage: Inserts entries from Table 2 into separate table
"""


def child_classify(table, file):
    file = file.split("_")[0]
    try:
        for i in range(1, len(table)):
            table_list = [file]
            for j in range(0, len(table[0])):
                table_list.append(table[i][j])
            sql_query = ("insert into dbo.pd_minute_order_counts ({})\
                             values (%s,%s,%s,%s,%s,%s,%s,%s)".format(t2_columns_str))
            cursor.execute(sql_query, table_list)
            db.commit()
    except IndexError:
        logging.info("Error: Incorrectly formatted table")
        return
    except pymssql.DatabaseError:
        db.rollback()
        logging.info("Error: Could not classify for Table 2")
        return


"""
Usage: Prepares tables for classification functions depending on how many tables exist in the pdf
Returns: All values returned from Table 1 and the point where it ends
"""


def table_search(tables, path, file):
    t1_data = tables[0].extract()
    if '' in t1_data[3]:
        t1_data.remove(t1_data[3])
    main_classify(t1_data)
    logging.info("Main table stored for {}.".format(file))
    table_end = pymupdf.Rect(tables[0].bbox)
    if len(tables.tables) > 1:
        t2_data = tables[1].extract()
        table_end = pymupdf.Rect(tables[1].bbox)
        child_classify(t2_data, file)
        logging.info("Second table stored for {}.".format(file))
    return table_end


"""
Usage: Searches for new bolded keywords and adds them to columns + classes
"""


"""def find_new_class(blocks):
    global columns_str
    temp = ""
    for b in blocks:
        for l in b["lines"]:
            for s in l["spans"]:
                if s["flags"] == 2 ** 4:
                    curr = s["text"]
                    if s["text"][-1:] == ' ':
                        temp += s["text"]
                        continue
                    else:
                        temp += s["text"]
                        temp = ''.join(temp)
                        if temp not in main_classes:
                            main_classes.append(temp)
                        entry = temp.replace(' ', '')
                        if entry not in body_columns:
                            body_columns.append(entry)
                            body_content.append('')
                            columns_str += (', ' + entry)
                            sql_query = ("alter table dbo.pd_minute_orders \
                                                      add {} varchar(MAX)".format(entry))
                            cursor.execute(sql_query)
                            db.commit()
                            logging.info("Added new class {} to global class list.".format(temp))
                        temp = """""


"""
Usage: Combine all content into each category
"""


def concatenate(text):
    text_split = text.splitlines()
    for chunk in text_split:
        chunk.strip()
    text_str = ''.join(repr(text_split))
    line = 3
    try:
        while line < len(text_split):
            if text_split[line][-1:] == ' ':
                curr = text_split[line] + text_split[line + 1]
                line += 1
            else:
                curr = text_split[line]
            index = 10
            if curr in main_classes:
                index = main_classes.index(curr)
                body_content[index] += text_split[line + 1]
            else:
                body_content[index] += curr
            line += 1
    except IndexError:
        logging.info("Error: list sizes do not match at iteration " + str(line))


"""
Usage: Separates content from all pages into categories and content using global lists
"""


def scraper(path, file):
    with pymupdf.open(path) as pdf:
        logging.info("{} opened.".format(file))
        text = chr(12).join(i.get_text() for i in pdf)
        for num in range(0, len(pdf)):
            page = pdf[num]
            if not re.search('[a-zA-Z]', text):
                logging.info("{} is not OCR scanned.".format(file))
                return
            else:
                try:
                    tables = page.find_tables()
                    if len(tables.tables) > 0:
                        table_end = table_search(tables, path, file)
                        notes_box = page.rect
                        notes_box.y0 = table_end.y1
                        note_blocks = page.get_text("dict", flags=11, clip=notes_box)["blocks"]
                        notes = page.get_text(flags=2, clip=notes_box)
                    else:
                        note_blocks = page.get_text("dict", flags=11)["blocks"]
                        notes = page.get_text(flags=2)
                    # find_new_class(note_blocks)
                    concatenate(notes)
                except IndexError:
                    logging.info("Error: Only one or no table found")
                    return
        if len(body_columns) == len(body_content):
            db_send(body_columns, body_content)
            logging.info("{} stored into database.".format(file))


def db_send(columns, values):
    try:
        format_list = []
        format_str = ', '.join(columns)
        sql_query = "insert into dbo.pd_minute_orders ({}) values ()".format(format_str)
        for i in range(0, len(values)):
            format_list.append('%s')
        format_str = ','.join(format_list)
        insert_query = sql_query[:-1] + format_str + sql_query[-1:]
        cursor.execute(insert_query, values)
        db.commit()
    except pymssql.Error:
        db.rollback()
        logging.info("Error: Could not send final query.")


"""
Usage: Iterate through CourtMinutes
Output: None
"""


def run():
    global body_columns, body_content
    cursor.execute("select * from dbo.pd_minute_orders")
    body_columns = [item[0] for item in cursor.description]
    for item in range(10, len(body_columns)):
        split_words = re.findall('[A-Z][^A-Z]*', body_columns[item])
        item_str = ' ' .join(split_words)
        main_classes.append(item_str)

    df = pd.read_excel("Court Minutes.xlsx", sheet_name='Sheet3')
    logging.info("Opened CourtMinutes.xlsx.")
    paths = df['File']
    names = df['File Name']
    for i in range(len(names)):
        if ".pdf" in names[i]:
            for j in range(0, len(body_columns)):
                body_content.append('')
            scraper(paths[i], names[i])
            body_content = []


run()
cursor.close()
db.close()

end = time.time()
logging.info("scrape.py completed in " + str((end - start) / 60) + " minutes.")
