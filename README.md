## About

This Python script takes an Apache-formatted access/request log as an argument, and issues bans that match specific conditions.  Filters are created for each condition, and inside of those filters, counts and timestamps are tracked of each IP address that matches the condition.  As the entry times age out of the tracked period of each filter, the entries are removed, therefore reducing the amount of data stored in memory, and reducing the time it takes to iterate through the dictionary of timestamps.  On my laptop, this script ran and produced a CSV output in 2.64 seconds.

## Use

In order to run this script, download `main.py` and `requirements.txt`.  Install dependencies via `pip install -r requirements.txt`.  To execute the script, pass the log file a command-line argument: `python3 main.py <FILE_NAME>`.  The script will output `<FILE_NAME>.csv` in the directory where the script file is located.
