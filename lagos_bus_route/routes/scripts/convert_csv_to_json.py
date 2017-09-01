import json
import os
import sys

from report_node_to_busstop_mismatch import read_csv_file


DEFAULT_OUTFILE_NAME = 'nodes.json'
FIELDNAMES = ('busstop', 'busstop_type', 'route_id', 'node_position')


def convert_csv_to_json(csvfile, outfile):
    """Convert rows items/objects in a json file

    :param csvfile: name of csv file
    :param outfile: filepath to save json
    """
    route_to_busstop_table = read_csv_file(csvfile)
    routes = []
    route_id = 1
    node_position = 1
    for row in route_to_busstop_table:
        routes.append({
            'busstop': row['busstop_id'],
            'node_type': row['node_type'],
            'route_id': route_id,
            'node_position': node_position
        })

        if row['node_type'] == 'TE' and node_position > 1:
            node_position = 1
            route_id += 1
            continue

        node_position += 1

    with open(outfile, 'w') as file:
        json.dump(
            routes, file, sort_keys=True, indent=4, separators=(',', ': ')
        )
        print('File successfully saved')


def main():
    if len(sys.argv) < 2:
        sys.exit('You forgot to pass a file name')

    csvfile = sys.argv[1]
    if not os.path.exists(csvfile):
        sys.exit('The file name does not exist')

    app_path = os.path.dirname(os.getcwd())
    jsonfile = '{app_path}/fixtures/{filename}'
    jsonfile_name = 'routes.json'
    if len(sys.argv) == 3:
        jsonfile_name = sys.argv[2]
    jsonfile = jsonfile.format(app_path=app_path, filename=jsonfile_name)

    convert_csv_to_json(csvfile, jsonfile)


if __name__ == '__main__':
    main()
