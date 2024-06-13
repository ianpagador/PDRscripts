import os, logging
import time
import pymssql

start = time.time()

try:
    db = pymssql.connect(
        server='{REDACTED}',
        user='{REDACTED}',
        password='{REDACTED}',
        database='{REDACTED}',
        port='{REDACTED}'
    )
    cursor = db.cursor()
except pymssql.Error:
    print("Error: Unable to connect to SQL server")

"""
Execution: 4 instances concurrently, 6 assigned folders each

1. In C:\\Test\\CourtMinutes, pull case no. between 'CRI-' and '_'
2. SQL call using stored court no. to get dest folder (if exists)
3. Error handling in case it doesn't exist
4. Move file starting CRI to dest folder

Move CRI files from C:\\Test\\CourtMinutes\\YYYYMM to C:\\Test\\LNAME-FNAME-CaseNo\\Minutes
If Minutes does not exist yet, create that folder
"""

logger = logging.getLogger(__name__)
logging.basicConfig(filename='move_min.log', level=logging.INFO, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info("move_min.py started.")

"""
Input: Extracted court number
Output: Formatted court number (8 digits)
Function: Formats CRI
"""


def court_no(input):
    zeros = "00000000"
    output = zeros[: - len(input)] + input
    return output


"""
Input: Case number
Output: Matching directory path
Function: Finds corresponding folder if it exists
"""


def find_case(court_no, src_path, name):
    try:
        sql_query = ("select case_folder = dbo.fn_case_folder(id) "
                     "from cms_case "
                     "where courtno = %s")
        cursor.execute(sql_query, court_no)
        case_folder = str(cursor.fetchone()).split('\'')[1]
        # print(case_folder, '\n', src_path)
        dest_path = "C:\\Test\\{}\\Minutes".format(case_folder)
        if not os.path.isdir(dest_path):
            os.makedirs(dest_path, exist_ok=True)
            logging.info("Created {} directory".format(dest_path))
    except pymssql.DatabaseError:
        logging.info("Error: Could not communicate with SQL server")
        return
    except IndexError:
        logging.info("Error: SQL entry {} not found".format(court_no))
        return

    try:
        os.rename(src_path, dest_path + '\\' + name)
        logging.info("Moved {} to {}".format(name, dest_path))
    except FileExistsError:
        logging.info("Error: Could not move file ", name)
        return
    except FileNotFoundError:
        logging.info("Error: File not found: ", name)
        return


"""
Input: Path to folder for specific month
Function: Extracts CRI and passes it to formatting function
"""


def cri_extract(path):
    for entry in os.scandir(path):
        name = entry.name
        info_list = name.split("_")
        try:
            if not info_list[0].isdigit():
                cri = info_list[0].split("-")
                digits = court_no(cri[1])
            else:
                digits = court_no(info_list[0])
            find_case(digits, path + "\\" + name, name)
        except IndexError:
            logging.info("Error: Could not extract CRI from ", str(name))
            pass


"""
Modify for loop, only need certain range since multiple will be running
Function: Runs necessary functions for each month folder
"""


def minutes():
    root = "C:\\Test\\CourtMinutes"
    # cri_extract(root + "\\202211")
    for folder in os.listdir(root):
        path = root + "\\" + folder
        cri_extract(path)


minutes()

cursor.close()
db.close()

end = time.time()
logging.info("move_min.py completed in " + str((end - start) / 60) + " minutes.")
