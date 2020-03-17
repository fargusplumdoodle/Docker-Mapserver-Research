#!/usr/bin/python3
import csv
import sys
import re
import os
import datetime
from analyze_jmeter import AnalyzeJmeter

documentation = """
----------------------
    ANALYZE DSTAT
----------------------

"""


class AnalyzeDstat(object):
    def __init__(self, csv_path):
        self.time_events, self.cpu_event, self.mem_event, self.load_event = self.get_system_usage(csv_path)

    def get_system_usage(self, dstat_csv):
        """
            This function extracts the following attributes from the dstat
            CPU Usage (%) for each second
            Memory Usage (GB) for each second

            The timestamp assumes that this script was ran in the same year as when you ran dstat.
            Dstat doesn't include the year in its timestamp so we have to add the current year in
            order to determine the ctime of the event.
            """
        # opening CSV file
        with open(dstat_csv, "r") as csv_file:
            # loading csv file
            csv_reader = csv.reader(csv_file)

            # getting data as list
            data = [x for x in csv_reader]

            headers = None
            header_location = None
            # dstat adds a bunch of useless information at the top of the csv file, so we cannot assume the headers
            # are at line 0
            for x in range(len(data)):
                # finding headers
                try:
                    if data[x][0] == "time":
                        header_location = x
                        headers = data[x]
                except IndexError:
                    # for the first few rows, there arn't any tuples
                    pass
            if header_location is None:
                raise ValueError("Unable to find headers in CSV. Looking for: ", headers)

            # each row in the csv will translate to one item in each of these lists
            # they should all be the same length
            time_events = []  # the X axis for the following two attributes
            cpu_event = []  # for tracking CPU usage
            mem_event = []  # for tracking amount of RAM usage
            load_event = []
            for row in data[header_location + 1:]:
                # GETTING ATTRIBUTES FROM DSTAT OUTPUT

                # need time in ctime
                # Dstat provides time in this format: "04-11 10:29:56"
                # We need to add the year in order to get the ctime
                time = row[headers.index("time")] + " " + str(datetime.date.today().year)
                # adding time in C time format to event
                time_events.append(
                    int(datetime.datetime.strptime(time, "%d-%m %H:%M:%S %Y").timestamp())
                )

                # getting CPU usage for this time
                # The data is given in "idle" percentage, so 60 means 60% of the CPU is unused. We want the usage
                # so we take 100 - idl to give us the amount of resources that are used
                cpu_event.append(round(100 - float(row[headers.index("idl")])))

                # getting the memory usage in GB
                mem_event.append(round(float(row[headers.index("used")])) / 1000_000_000)

                # getting load average over last minute
                load_event.append(float(row[headers.index("1m")]))

        return time_events, cpu_event, mem_event, load_event

