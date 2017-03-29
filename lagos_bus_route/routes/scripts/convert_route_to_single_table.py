import csv

read_file = 'raw_routes.csv'
write_file = 'processed_routes.csv'


def read_column(column_number):
    '''Read a single column at a time
    Although this may be inefficient. It is much simpler than trying
    to go through each row once and saving the each column separately.
    The fact that this is a one-off script also doesn't justify any
    more complexity.
    '''
    column = []
    with open(read_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[column_number] == '':
                break
            column.append(row[column_number])
    return column


def write_column(column):
    '''Write column to csv file, each busstop occupying
    a row along with its bus stop type i.e. TE or TR
    '''
    size = len(column)
    for count, busstop in enumerate(column):
        with open(write_file, 'aw') as csvfile:
            writer = csv.writer(csvfile)
            busstop_type = 'TE' if count == 0 or count == size - 1 else 'TR'
            writer.writerow([busstop, busstop_type])


def convert_route_to_single_table():
    num_columns = 81
    for column_number in xrange(num_columns):
        column = read_column(column_number)
        write_column(column)


if __name__ == '__main__':
    convert_route_to_single_table()
