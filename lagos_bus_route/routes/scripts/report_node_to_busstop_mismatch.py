"""This would be run as a django command"""

import csv
import os
import parser
import pprint
import sys
import warnings


FIELDNAMES = ('node_name', 'node_type', 'busstop_name', 'busstop_id')


def read_csv_file(filename):
    """Reads the csv file and returns a dict
    :param filename: name of csv file (string)
    :return: a DictReader object
    """
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=FIELDNAMES, delimiter=',')

        for row in reader:
            yield row


def generate_node_to_busstop_mismatch_report(filename):
    """
    Iterate over node to busstop file and notes where the node and busstop
    are not an exact match
    :param filename: name of csv file (string)
    :return: a dictionary of all mismatches
    """
    mismatches = {}
    node_to_busstop_table = read_csv_file(filename)
    for line_no, row in enumerate(node_to_busstop_table, start=1):
        if row['node_name'] != row['busstop_name']:
            row.update({'line_no': line_no})
            mismatches.update(row)
    return mismatches


def main():
    if len(sys.argv) < 2:
        sys.exit('You forgot to pass a file name')

    filename = sys.argv[1]
    if not os.path.exists(filename):
        sys.exit('The file name does not exist')

    mismatches = generate_node_to_busstop_mismatch_report(filename)
    pprint.pprint(mismatches)


if __name__ == '__main__':
    main()
