"""
Generate Test Results
----------------------
Input:
    list of report directories that have already completed
    This is from a YML file located in "./scripts/report_list.yml"
    Every time a new report is made it is added to that list
Output:
    test_results.csv
    A CSV file with all of the attributes from all of the reports.

For information about the CSV file look at "docs/load_test_attribute_definitions.txt" it has
a description for each collumn in this output file.
"""
import os
import csv
from analyze_report import generate_stats
import yaml

REPORT_LIST = "./scripts/report_list.yml"

OUTPUT_FILE_PATH = "./test_results.csv"


def load_reports(report_list):
    """
    This function loads a list of report directories from the REPORT_LIST yaml file
    :param report_list: path to report list.yml
    :return: list of report directories
    """
    reports = None
    with open(report_list, 'r') as fl:
        reports = yaml.load(fl)['reports']

    return reports


def generate_test_results(output_file, report_dirs):
    # 1. Validate input
    if len(report_dirs) < 1:
        raise ValueError("Require at least one report directory")
    for x in report_dirs:
        if not os.path.isdir(x):
            raise ValueError(f"{x} is not a directory")

        if not os.path.isfile(os.path.join(x, 'jmeter.csv')):
            raise ValueError(f"{x}/jmeter.csv does not exist")

        if not os.path.isfile(os.path.join(x, 'dstat.csv')):
            raise ValueError(f"{x}/dstat.csv does not exist")

    # 2. Getting statistics from each report
    reports = []
    for report in report_dirs:
        reports.append(generate_stats(report))

    # 3. generating header for CSV
    #   headers are the keys in the stat object, they are all the same so we
    #   only look at the first
    header = [x for x in reports[0]]

    with open(output_file, 'w') as csv_fl:
        writer = csv.writer(csv_fl)
        # writing header
        writer.writerow(header)

        # writing rows
        for stats in reports:
            # row is a dictionary, we just need to get the values
            row = []
            for x in stats:
                row.append(str(stats[x]))
            writer.writerow(row)


if __name__ == '__main__':
    generate_test_results(OUTPUT_FILE_PATH, load_reports(REPORT_LIST))
