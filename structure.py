import os, logging
import time

start = time.time()

logger = logging.getLogger(__name__)
logging.basicConfig(filename='structure.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info("structure.py started.")
path = "C:\\Test"

def perms(folder, group):
    # os.system('icacls {} /grant "Administrators":(F)'.format(folder))
    for member in group:
        # print('icacls {} /grant "{}@EXAMPLEDIRECTORY.org":(R,W)'.format(folder, member))
        os.system('icacls {} /grant "{}@EXAMPLEDIRECTORY.org":(R,W)'.format(folder, member))
        logging.info('Permissions for {} limited to read and write for {}.'.format(folder, member))

def create(details):
    # perms_list = ['Domain Admins','Administrator','Unit Clerical']
    perms_list = ['Domain Admins']
    folder_list = ['\\Records','\\Records\\Media','\\Minutes','\\Work']
    title = path + "\\dest_task1_testSuite\\{}".format(details)
    # os.makedirs(title, exist_ok=True)
    # perms(title, ['Domain Admins','Administrator'])
    # logging.info(title + " directory created.")
    for folder in folder_list:
        if not os.path.exists(title):
            os.makedirs(title + folder, exist_ok=True)
        os.system('icacls ' + title + folder + ' /inheritancelevel:r')
        perms(title + folder, perms_list)

    """
    # print('icacls "{}" /save "{}\\defense_teams.txt"'.format(title, path))
    os.system('icacls "{}" /save "{}\\defense_teams.txt"'.format(title, path))
    # print('icacls "{}\\Work" /restore {}\\defense_teams.txt'.format(title, path))
    os.system('icacls "{}\\Work" /restore "{}\\defense_teams.txt"'.format(title, path))
    # print('icacls "{}" /grant:r "{}":(OI,CI)'.format(title + '\\Work', title))
    # os.system('icacls "{}" /grant:r "{}":(OI,CI)'.format(title + '\\Work', title))
    """

def iter():
    for entry in os.scandir(path + "\\dest_task1_testSuite"):
        # temp since CourtMinutes is in src folder
        if entry.name == "CourtMinutes":
            pass
        # Keep everything after here
        details = entry.name
        create(details)


iter()
# find_process()

logging.info("structure.py completed.")
end = time.time()
logging.info("Runtime: " + str((end - start) / 60) + " minutes")
