import sys
import os
import datetime
import re
from Graph import render_graph
from analyze_dstat import AnalyzeDstat
from analyze_jmeter import AnalyzeJmeter

DOCUMENTATION = """
ANALYZE REPORT
--------------
Arguments: 
    1. Path to reports directory
        - must follow pattern: ./reports/h<host id>/<test_name>
        - test_name must follow convention:
            <test_plan>[_<value>attribute ...]
            example: official_4mp_2cores
            - Attributes are seperated by underscores '_'

        The current attributes are:
            - mp: Max Processes, default: 5
            - mrpp: Max Request Per Process, default: 1000
            - cores: Virtual CPU cores on host, default: 2
            
        If the attributes are omitted, this will set their values            
        Examples: 
            official_5mp_1500mrpp_2cores
            extreme_10mp_1000mrpp
            extreme
            
This script analyzes the output of the load test:
    looks for:
        dstat.csv 
        jmeter.csv
    
    creates:
        stats.txt: summary of statistics from test
        graph.png: a graph of the CPU and RAM usage during the test
"""


def print_stats(output_stats, iterable, title, units):
    """
    Prints statistical info on list
    :param output_stats: <path to report>/stats.txt
    :param iterable: any iterable with numerical elements
    :param title: the name of the iterable
    :param units: The unit of the iterable
    """
    with open(output_stats, 'a') as fl:
        fl.write("\n--------------------\n")
        fl.write("%s STATS\n" % title)
        fl.write("--------------------\n")
        fl.write("Units: %s\n" % units)
        fl.write("Min/Max Values: %.2f/%.2f\n" % (min(iterable), max(iterable)))
        fl.write("Average Value: %.2f\n" % (sum(iterable) / len(iterable)))


def get_container_settings_from_test_name(test_name):
    """
    The test names follow this convention:
        <test plan>_[attributes, ...]

        Attributes are seperated by underscores '_'

        The current attributes are:
            - mp: Max Processes, default: 5
            - mrpp: Max Processes, default: 1000
            - cores: Max Processes, default: 2

    :param test_name: name of test e.g. official_5mp
    :return: {
        'test_plan': 'official',
        'mp': 5,
        'mrpp': 1000,
        'cores': 2
    }
    """
    split_test_name = test_name.split('_')

    # defining regular expressions for finding attributes
    # these just find the number in front of the
    mp_regex = r'(\d+)mp'
    mrpp_regex = r'(\d+)mrpp'
    cores_regex = r'(\d+)core'

    attribute_regex = {
        'mp': re.compile(mp_regex),
        'mrpp': re.compile(mrpp_regex),
        'cores': re.compile(cores_regex),
    }

    data = {'test_plan': split_test_name[0]}

    default_values = {
        'mp': 5,
        'mrpp': 1000,
        'cores': 2,
    }

    # looping through attributes
    for attribute in split_test_name[1:]:
        # looping though regular expressions to try and
        # find if this attribute matches one of the known ones
        for regex_name in attribute_regex:
            # checking if this is the right attribute
            match = attribute_regex[regex_name].match(attribute)
            # this attribute matched! Lets save its value in our return
            #   data structure
            if match:
                data[regex_name] = int(match.group(1))

    # adding default values
    for attribute in default_values:
        if attribute not in data:
            data[attribute] = default_values[attribute]

    return data


def create_stats_file(stats_file, stats):
    """
    Creates the stats.txt file in the reports directory
    :param stats_file: path to "stats.txt"
    :param stats: stats object from "generate_stats" function. More info in 
        docker-mapserver/test/load_testing/doc/load_test_attribute_definitions.txt
    """
    with open(stats_file, 'w') as fl:
        fl.write("ANALYSIS OF LOAD TEST\n")
        fl.write("For more info read: docker-mapserver/test/load_testing/doc/load_test_attribute_definitions.txt\n\n")
        fl.write("----------------------\n\n")
        fl.write("INFO:\n")
        for stat in stats:
            # making a nicer output
            pretty_stat = ' '.join([x.capitalize() for x in str(stat).split('_')])
            fl.write(pretty_stat + ": " + str(stats[stat]) + "\n")
        fl.write("----------------------\n")


def get_hostname_and_test_name(report_dir):
    """
    This takes the path of the report directory and determines the hostname and testname
    :param report_dir: path to the report directory
    :return: hostname, testname
    """
    # getting test name and host number
    path_list = []
    for x in report_dir.split('/'):
        if x != '' and x != '.':
            path_list.append(x)
    if path_list[0] != "reports":
        raise ValueError("Path must be a subdirectory of the reports directory. Example input: ./reports/h1/official")
    # this only works if the directory structure is
    #   ./reports/<host name>/<test name/
    return path_list[1], path_list[2]


def generate_stats(report_path, create_file=False, create_graph=False, show_graph=False):
    """
    This function generates all of the statistics from the report and condenses it into a single dict object
    The stat object attributes are well defined in the "doc/load_test_attribute_definitions.txt" file

     Procedure:
            1. Create paths for all of the files and verify they exist
            2. Get data from jmeter.csv and dstat.csv
            3. Get information about test (test name, hostname)
            4. Generate stats
            5. Create stats file
            6. render graph

    :param report_path: path to report directory
    :param create_file: bool, to create the "stats.txt" file in the report directory
    :param create_graph: bool, to create the "graph.png" file in the report directory
    :param show_graph: bool, to show the graph after generation
    :return: stats object
    """
    # 1. defining files we want to use
    jmeter_csv = os.path.join(report_path, "jmeter.csv")
    dstat_csv = os.path.join(report_path, "dstat.csv")
    stats_file = os.path.join(report_path, "stats.txt")
    graph_file = os.path.join(report_path, "graph.png")

    # more input validation
    if not os.path.isfile(jmeter_csv):
        raise ValueError(f"Unable to find jmeter.csv in  {report_path}")
    if not os.path.isfile(dstat_csv):
        raise ValueError(f"Unable to find dstat.csv in  {report_path}")

    # 2. Get data from jmeter.csv and dstat.csv
    dstat = AnalyzeDstat(dstat_csv)
    jmeter = AnalyzeJmeter(jmeter_csv)

    # 3. Get information about test
    host, testname = get_hostname_and_test_name(report_path)
    test_attributes = get_container_settings_from_test_name(testname)

    # 4. generate stats on report
    # these are all well described in "docs/load_test_attribute_definitions.txt"
    stats = {
        "date": datetime.datetime.now(),
        "host": host,
        "test_name": testname,
        "duration": jmeter.get_duration_of_test(),
        "failure_rate ": jmeter.get_failure_rate(),
        "test_plan": test_attributes['test_plan'],
        "max_processes": test_attributes['mp'],
        "max_requests_per_process": test_attributes['mrpp'],
        "cpus": test_attributes['cores'],
        "cpu_avg_usage": round(sum(dstat.cpu_event) / len(dstat.cpu_event), 2),
        "cpu_max_usage": max(dstat.cpu_event),
        "cpu_min_usage": min(dstat.cpu_event),
        "mem_avg_usage": round(sum(dstat.mem_event) / len(dstat.mem_event), 2),
        "mem_max_usage": round(max(dstat.mem_event), 2),
        "mem_min_usage": round(min(dstat.mem_event), 2),
        "load1m_avg": round(sum(dstat.load_event) / len(dstat.load_event), 2),
        "load1m_max": round(max(dstat.load_event), 2),
        "load1m_min": round(min(dstat.load_event), 2),
        "latency_avg": round(sum(jmeter.latency) / len(jmeter.latency), 2),
        "latency_max": round(max(jmeter.latency), 2),
        "latency_min": round(min(jmeter.latency), 2),
        "total_requests": jmeter.num_requests,
        "throughput": jmeter.throughput,
    }

    # setting up stats file
    if create_file:
        create_stats_file(stats_file, stats)

    # rendering graph
    if create_graph:
        render_graph(graph_file, dstat.time_events, dstat.cpu_event, dstat.mem_event, dstat.load_event, show=show_graph)

    return stats


if __name__ == "__main__":
    """
        Procedure:
            1. Validate input
            2. generate statistics, creating the graph.png file and stats.txt file
    """
    # 1. Validate input
    if len(sys.argv) != 2:
        print(DOCUMENTATION)
        exit(-2)
    # ensuring output directory exists
    if not os.path.isdir(sys.argv[1]):
        raise ValueError(f"Output directory {sys.argv[1]}, not a directory")

    report_path = sys.argv[1]

    # creating stats file
    stats = generate_stats(report_path, create_file=True, create_graph=True)
