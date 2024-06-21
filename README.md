# PDRscripts

All of my completed scripts as a PDR IT intern (with sensitive/confidential information redacted).

## move_min.py
Moves court documents from a directory with subfolders partitioned by month to their respective folder formatted as follows: FIRSTNAME-LASTNAME-COURTNO. Utilizes a SQL server to find full name information based on court document titles.

### Test runtimes
| Test # | Files    |  Duration    |
| ------ | -------- | ------------ |
| 1      |  3,045   |  18 minutes  |
| 2      |  13,665  |  77 minutes  |
| 3      |  10,599  |  63 minutes  |

## scrape.py
Reads through court documents from locations provided through a "Court Minutes" Excel document using PyMuPDF. Every document contains a table with 10 categories, and most have an additional table which displays offenses. Following the first two tables is a log of additional classifications which vary with each document. These entries are appended to the SQL call for the main table. \\
This program scrapes values for each of these categories and stores them on two tables pd_minute_orders and pd_minute_order_counts with different structures on a SQL server using PyMSSQL.

### Test runtimes
| Test # | Files    |  Duration    |
| ------ | -------- | ------------ |
| 1      |  3,516   |  7.4 minutes |

## structure.py
Creates a subfolder structure for each FIRSTNAME-LASTNAME-COURTNO directory for Records, Records\Media, Minutes, and Work, all with different permissions. Uses icacls for command line prompts.
