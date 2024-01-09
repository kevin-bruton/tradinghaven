import time
from datetime import datetime, timedelta
from contracts import contract
import os

one_day_in_secs = 60*60*24
duration_td = timedelta(seconds=one_day_in_secs)
duration_str = str(one_day_in_secs) + ' S'

input_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/data/DAX-TS-TE_2023.12.25.csv"
output_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/data/DAX-TS-TE_2023.12.25_fixed.csv"

"""
# Remove first column that included the symbol name on every line
with open(input_filepath) as in_f:
    with open(output_filepath, 'w') as out_f:
        for line in in_f:
            line_segments = line.split(',')
            line_segments.pop(0)
            new_line = ','.join(line_segments)
            out_f.write(new_line)
"""

# Change order or date/month in date format
with open(input_filepath) as in_f:
    with open(output_filepath, 'w') as out_f:
        for line in in_f:
            line_segments = line.split(',')
            date_str = line_segments[0]
            date_segments = date_str.split('/')
            new_date_str = f"{date_segments[1]}/{date_segments[0]}/{date_segments[2]},"
            new_line = new_date_str + ','.join(line_segments[1:])
            out_f.write(new_line)
