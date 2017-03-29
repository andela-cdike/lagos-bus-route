'''This would be run from terminal'''

import csv

from busstops.models import BusStop

ROUTE_FILE = 'routes/scripts/processed_routes.csv'
ROUTE_TO_BUSSTOP_FILE = 'routes/scripts/route_node_to_busstop.csv'
ONE_MATCH = 'routes/scripts/one_match.csv'
MULITIPLE_MATCHES = 'routes/scripts/multiple_matches.csv'
NO_MATCH = 'no_match.csv'
OLD_FIELDNAMES = ('busstop_name', 'busstop_type')
NEW_FIELDNAMES = (OLD_FIELDNAMES) + ('matches',)


def read_csv(filename):
    result = []
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=OLD_FIELDNAMES)
        for row in reader:
            result.append(row)
    return result


def write_to_file(filename, busstop, matches=[]):
    with open(filename, 'awb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=NEW_FIELDNAMES)
        matched_busstop = '|'.join(
            ['{0},{1}'.format(match.name, match.id) for match in matches]
        )
        writer.writerow({
            'busstop_name': busstop['busstop_name'],
            'busstop_type': busstop['busstop_type'],
            'matches': matched_busstop,
        })


def map_route_nodes_to_busstop_in_db():
    routes = read_csv(ROUTE_FILE)
    for busstop in routes:
        matched = BusStop.get_queryset(busstop['busstop_name'], '')
        write_to_file(ROUTE_TO_BUSSTOP_FILE, busstop, matched)
