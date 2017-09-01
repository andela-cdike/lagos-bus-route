"""This would be run as a django command"""

import os
import sys
import warnings


from report_node_to_busstop_mismatch import read_csv_file


def find_busstop_id_greater_than_max(filename, max_valid_id):
    """Find busstops in csv file that have an id
    greater than the current known max in db
    """
    node_to_busstop_table = read_csv_file(filename)
    for line_no, row in enumerate(node_to_busstop_table):
        if int(row['busstop_id']) > max_valid_id:
            msg = 'Invalid busstop id of {0} found on line: {1}'
            warnings.warn(msg.format(row['busstop_id'], line_no))


def main():
    if len(sys.argv) < 3:
        sys.exit('You forgot to pass a file name and/or maximum valid busstop Id')

    max_valid_id = int(sys.argv[2])
    filename = sys.argv[1]
    if not os.path.exists(filename):
        sys.exit('The file name does not exist')

    find_busstop_id_greater_than_max(filename, max_valid_id)


if __name__ == '__main__':
    main()
