import logging
import os
import subprocess as sp
import time

r"""
Open Cases, currently stored on Synology as NFS:
    A-L: \\10.60.105.102\PDR-Open-Cases\A-L
    N-Z: \\10.60.105.103\OpenCases-M-Z

2-way sync to here: \\pdr-files\cases
    The root folder has two permission levels
        Domain Users = read/write
        Domain Admins = full control

Folder structure should be:
    \\pdr-files\cases\attorneylastname-attorneyfirstinitial

Folders below that, keep the structure of what is in Open Cases

Any folders added under the attorneylastname-attorneyfirstinitial, should allow domain users to modify, but not full control.

We want users to have full control of the sub-folder but not mess with the root folder

Sync hourly

My goal is to decommission the Open Cases stored on the Synology and have people go directly to the SF Cloud one at PDR-Files.
"""

start = time.time()

logger = logging.getLogger(__name__)
logging.basicConfig(filename='initDirs2.log', level=logging.INFO, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info("initDirs.py started.")

# Test environment
root_list = [r"C:\Users\ipagador\PycharmProjects\openCasesSync\testRoot1", r"C:\Users\ipagador\PycharmProjects\openCasesSync\testRoot2"]
dest = r"C:\Users\ipagador\PycharmProjects\openCasesSync\testDest"

# root_list = [r"\\10.60.105.102\PDR-Open-Cases\A-L", r"\\10.60.105.103\OpenCases-M-Z"]
# dest = r"\\10.250.7.145\cases"

def set_perms(dest_path, p_dict):
    """
    SYNTAX:
    Full control: (OI)(CI)(F)
    Read-only: (OI)(CI)(RX)
    Read and write: (OI)(CI)(M)
    """
    for subdir in os.scandir(dest_path):
        if subdir.is_dir():
            try:
                # print(folder)
                sp.run(['icacls', subdir.path, '/grant', 'SYSTEM:F'],
                       stdout=sp.DEVNULL, stderr=sp.STDOUT)
                logging.info('SYSTEM granted full permissions for {}.'.format(subdir.path))
                for key in p_dict.keys():
                    sp.run(['icacls', subdir.path, '/grant:r', '{}@pubdef.sfgov.org:{}'.format(key, p_dict[key])],
                           stdout=sp.DEVNULL, stderr=sp.STDOUT)
                    logging.info('MAIN DIRECTORIES: {} access for {} given to {}.'.format(p_dict[key], subdir.path, key))
                sp.run(['icacls', subdir.path, '/grant', 'Domain Users@pubdef.sfgov.org:(OI)(CI)(M)'],
                       stdout=sp.DEVNULL, stderr=sp.STDOUT)
                logging.info('SUBDIRECTORIES: M access for {} subfolders given to Domain Users.'.format(subdir.path))
            except sp.CalledProcessError as e:
                logging.error(e.output)
                pass


def copy_robo(root, dest):
    try:
        result = sp.run(['robocopy', root, dest, '/E', '/Z', '/COPY:DAT', '/NP'],
                        stdout=sp.DEVNULL, stderr=sp.STDOUT)
        if result.returncode != 0:
            logging.error(result.stdout)
        else:
            logging.info("SUCCESS: Moved all contents of {} to {}".format(root, dest))
    except sp.CalledProcessError as e:
        logging.error(e.output)
        pass

def main():
    p_dict = {
        "Domain Admins": "F",
        "Domain Users": "RX",
    }
    for root in root_list:
        copy_robo(root, dest)
    set_perms(dest, p_dict)


main()

logging.info("initDirs2.py completed.")
end = time.time()

print("Runtime: ", (end - start) / 60, " minutes")
