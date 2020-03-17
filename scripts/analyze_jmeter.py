import csv
import sys
import os

"""
Analyze Jmeter
--------------

input: jMeter log csv
outputs: stats

Implemented:
    - duration of test
    - latency
    - failed request percentage
Unimplemented:
    - throughput?? hopefully I can figure out how to do this?
"""


class AnalyzeJmeter(object):
    def __init__(self, csv_path):
        self.data = self.load_jmeter_csv(csv_path)
        self.latency = [x / 1000 for x in self.data['elapsed']]
        self.num_requests = self.get_number_of_requests()
        self.throughput = self.get_throughput()

    def load_jmeter_csv(self, csv_path):
        """
        :param csv_path: path to jmeter CSV on disk
        :return: headers, data
                headers: list of headers
                data: list of datapoints in a 2 dimentional array
        """
        if not os.path.isfile(csv_path):
            raise OSError("jmeter CSV does not exist")

        # defining headers
        headers = ["timeStamp", "elapsed", "label", "responseCode", "responseMessage", "threadName", "dataType",
                   "success", "bytes", "grpThreads", "allThreads", "Latency"]

        # these columns will be converted to int before storing in memory
        int_fields = ["timeStamp", "elapsed", "bytes", "grpThreads", "allThreads", "Latency"]

        # defining data structure to return
        data = {}
        for header in headers:
            data[header] = []

        # opening CSV file
        with open(csv_path, "r") as csv_file:
            # loading csv file
            csv_reader = csv.reader(csv_file)
            raw_data = [x for x in csv_reader]

            # adding data to return data
            for row in range(len(raw_data)):
                for col in range(len(raw_data[row])):

                    # storing integers as ints instead of strings
                    if headers[col] in int_fields:
                        data[headers[col]].append(int(raw_data[row][col]))
                    else:
                        # all other data is stored as strings
                        data[headers[col]].append(raw_data[row][col])
        return data

    def get_number_of_requests(self):
        """
        :return: the total number of requests made during the test
        """
        return len(self.data["timeStamp"])

    def get_throughput(self):
        """
        :return: the number of requests per minute
        """
        return round((self.get_number_of_requests() / self.get_duration_of_test()) * 60, 2)

    def get_duration_of_test(self):
        """
        :return: the duration of the test in seconds
        """
        # total miliseconds elapsed
        ms = int(self.data['timeStamp'][-1]) - int(self.data['timeStamp'][0])
        seconds = ms / 1000
        return round(seconds, 2)

    def get_failure_rate(self):
        """
        :return: The percentage of failed responses
        """
        fails = 0
        for x in self.data['responseCode']:
            if x != "200":
                fails += 1

        return round(fails / len(self.data['responseCode']), 2) * 100


if __name__ == "__main__":
    jmeter = AnalyzeJmeter(sys.argv[1])

    print(
        jmeter.get_duration_of_test()
    )
