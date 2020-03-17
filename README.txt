---------------------------------
Load Testing script for Mapserver
---------------------------------
Isaac Thiessen, 2019-11-04

----------------------------------------------------------------------------------
# NOTE:
----------------------------------------------------------------------------------

This repository is a subset of a project I worked on  
for NFIS during my Co-op there.

I have recieved permission to publish this information
from my manager as long as I strip out all of the sensitive 
information.

Unfortunatley there has been a lot of sensitive information
that I have had to remove.

For the TL;DR of this whole project, refer to the "Load Testing Report.pdf"

----------------------------------------------------------------------------------

Purpose:
    To determine the resource impact of switching to Docker Mapserver oppose to keeping
    the existing infrastructure.

Background:
    Currently on NFIS servers, Mapserver is ran on the same host as the Apache instance. This is done by CGI scripts
    that call mapserver.

    The new purposed infrastructure would involve Apache acting as a reverse proxy to a Docker instance of mapserver.

Procedure Overview:
    This testing procedure involves a client and 2 servers. The client is the users machine running jMeter and the
    "analyze_dstat.py" script.

    The first server is a replication of NFIS's current system: running apache and mapserver on the same host.
    The second is the new proposed system, running apache and docker, while also running the mapserver docker image.

    The client will use "jMeter" to load test each of the servers, while "dstat" measures the system resources such as
    CPU and memory usage. Dstat will be ran through SSH from the client to both servers.

Setup:
    Package requirements for both servers:
        - apache
        - dstat

    Docker Server requirements:
        - Docker version 19.03.3

    Apache Server requirements:
        - Mapserver

    Client requirements:
        - SSH Access to both servers
        - jMeter
        - dstat ( for testing, not actually used in procedure)
        - python3
        - python-tk ( for showing matplotlib graphs )
        - pip3 packages:
            matplotlib
            numpy


Procedure:
    Note: The order that we test the servers is irrelevant and the procedure is the same for both.
    Note: Do not test both servers at the same time, running two instances of jMeter may skew results.

    0. Ensure all machines are setup with required dependencies.
	See: server_setup_procedure.txt
    1. Edit "MapserverJmeterTest.jmx" with Jmeter on the client to point to the first server.
        1.1 Open Jmeter and load "MapserverJmeterTest.jmx"
        1.2 Click on "HTTP Request Defaults" on the left panel (it's a child of "Test Plan")
        1.3 Change the "Server Name or IP" field to match the IP (or hostname) of the first server.

    2. Log into the first server through SSH and TYPE the following command, modifying if necessary:
       DONT RUN IT YET! For best results we need to run jMeter just after running dstat.

        "dstat --time --cpu --mem --load --output /tmp/dstat_host1.csv 1 110"

        Explanation:
            --time: include timestamps
            --cpu: include CPU usage info
            --mem: include memory usage info
            --load: include CPU load info
            --output /tmp/dstat_host1.csv: Output CSV file. If this is the second host, rename to /tmp/dstat_host2.csv
            1: Print one output per second
            110: Stop after this much time. This is set to 110 because the jMeter test currently runs for 100 - 104 seconds.
                 If you plan on changing the length of time that jMeter tests for, make sure to also change this number
                 to be slightly longer.

    3. In a separate terminal on the client, type in the following command. DONT RUN IT YET!

        <path_to_jmeter_executable> -t <path_to_MapserverJmeterTest.jmx> -n -l reports/jmeter_host1.csv

        Replace:
            <path_to_jmeter_executable>: the full path to the CLI executable for jMeter. Don't confuse with the GUI version
                                            we only want to run the CLI executable. For me its located at "bin/jmeter"
                                            from the jMeter install directory.
            <path_to_MapserverJmeterTest.jmx>: the configuration file edited in step 1.
            reports/jmeter_host1.csv: replace with reports/jmeter_host2.csv if you are going to test the second host.

         Explanation:
            -t: load config
            -n: run headless mode
            -l: set output report file

    4. As mentioned earlier: for best results we need to run jMeter just after running dstat. So try to quickly run
        dstat on the server (from step 2), then run jMeter on the client (from step 3). dstat records system usage,
        we want to record system usage during the jMeter test, therefor they must both be running at approximately the
        same time on both hosts.

        If dstat stops before jMeter completed, restart from step 2 and increase the run time for dstat (default is 110).
        There is no harm in "CTRL+C"-ing dstat when it is running, it will still create the same CSV file it would otherwise.
        If dstat runs too much longer than jMeter, force stop it with "CTRL+C".

    5. Once jMeter and dstat have finished running, download the CSV generated by dstat from the server

        scp <server_user>@<server_ip>:/tmp/dstat_host1.csv ./reports/dstat_host1.csv

        Replace:
            <server_user>: the user you ran dstat from
            <server_host>: the server that you most recently ran dstat from
            /tmp/dstat_host1.csv: change to wherever you set the output from dstat from step 2
            ./reports/dstat_host1.csv: change to host2 if you are connecting to the second host

    6. Repeat steps 1 to 5 replaceing every instance of host1 to host2. Make sure you connect to the server you didn't
        connect to last time.

    7. Analyze and compare results from the servers! With the "scripts/analyze_dstat.py" script. When you run these
        a window will popup showing graphs of system resources overtime. The terminal will hang until you close this
        window, or just CTRL+C to stop execution.

            "./scripts/analyze_dstat.py ./reports/dstat_host1.csv"
            "./scripts/analyze_dstat.py ./reports/dstat_host2.csv"

        Output should be similar too:

                --------------------
                CPU STATS
                --------------------
                Units: percent (%)
                Min/Max Values: 30.00/76.00
                Average Value: 42.94
                --------------------
                MEMORY STATS
                --------------------
                Units: Gigabytes (GB)
                Min/Max Values: 5.67/5.99
                Average Value: 5.91

         This is a summary of the system resources while undergoing the jMeter test. The graph shows the specific values
         over time.

Issues:
    Jmeter showing a lot of false negatives. If you are finding this error "Non HTTP response code: org.apache.http.NoHttpResponseException,Non HTTP response message:" in your jmeter csv
    you are getting this bug outline
    https://stackoverflow.com/questions/27942583/non-http-response-message-the-target-server-failed-to-respond-is-my-server-fai

