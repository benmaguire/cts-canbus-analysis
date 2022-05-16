# cts-canbus-analysis
Utilities for debugging canbus data

Python code to parse a candump or wireshark log from a canbus adapter and generate possible values of the data.
It uses pandas dataframes to hold and process data.

The original use case was to reverse engineer canbus data from a car and graph all possible data types so that they can be aligned by time in the graph output.
For example, if the break pedal was pressed at 5 seconds into the log, a graph output should exist showing this input and identify the CAN ID.

Usage: 

./canbus.py 

[Enter filename of log file]


The code will then output html files and images into out/ which show the results.



## Example candump to generate log file
candump -d -l can0

