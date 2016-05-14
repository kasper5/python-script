#!/usr/bin/env python
# Start Date : 2015-06-08
# End Date : 2015-06-
# Author : Kasper Fast
# Descritption :
# Version : 1.0

__author__ = 'Kasper Fast'

import csv
import sys
import os
import time
import re
import subprocess

# Get where csv file is located.
path = raw_input('Enter full path to file with domain names : ')

# Open it for reading.
open_cf = open(path, 'r')

# Read the csv file.
read_cf = csv.reader(open_cf)

def read_file(read_cf):

    def append_domain():

        # Create new list to store all domain names.
        domain_list = []

        # Append every domain to the list and join them with nothing.
        for line in read_cf:
            domain_list.append(" ".join(line))

        # Close csv file.
        open_cf.close()

        # Return the list.
        return domain_list

    domain_list = append_domain()

    active_list = [] # Used for active domains
    non_active_list = [] # Used for not active domains.

    for i in domain_list:

        print "Checking domain: %s..." % (i)
        # Execute whois command. Filter with awk/sed to get only date.
        whois_domain = subprocess.check_output("whois " + i + " | grep 'expire\|Expiration\|Expiry' | " \
                       "head -1 | awk -F':' '{print $2}' | sed 's/ //g'", shell=True)

        # If whois_domain is emtpy then the domain is not active. Append non,
        # active and active to separate lists.
        if not whois_domain:
            non_active_list.append(i)
        else:
            active_list.append(i)

        # For loop sleep for 2 seconds, to avoid WHOIS abuse.
        time.sleep(2)

    # Write list to files function.
    def write_file():

        # Creates file with all non active domains.
        for item1 in non_active_list:
            with open('non-active.txt', 'a') as non:
                non.write("NOT ACTIVE: %s\n" % item1)

        # Creates file with all active domains.
        for item2 in active_list:
            with open('active.txt', 'a') as act:
                act.write("ACTIVE: %s - Expire: %s\n" % (item2, whois_domain))

    write_file()

read_file(read_cf)

sys.exit(0)