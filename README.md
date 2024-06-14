# PDRscripts

## All of my completed scripts as a PDR IT intern (with sensitive/confidential information redacted).

## move_min.py
Moves court documents from a directory with subfolders partitioned by month to their respective folder formatted as follows: FIRSTNAME-LASTNAME-COURTNO. Utilizes a SQL server to find full name information based on court document titles.

### Test runtimes
| Test # | Files    |  Duration    |
| ------ | -------- | ------------ |
| 1      |  3,045   |  18 minutes  |
| 2      |  13,665  |  77 minutes  |
| 3      |  10,599  |  63 minutes  |

## scrape.py
Reads through court documents using PyMuPDF. Every document contains a table with 10 categories, and most have an additional table which displays listed misdemeanors. This program scrapes values for each of these categories, with tables 1 and 2 having different structures, and stores them on a SQL server in separate tables.

## structure.py
Creates a subfolder structure for each FIRSTNAME-LASTNAME-COURTNO directory for Records, Records\Media, Minutes, and Work, all with different permissions. Uses icacls for command line prompts.
