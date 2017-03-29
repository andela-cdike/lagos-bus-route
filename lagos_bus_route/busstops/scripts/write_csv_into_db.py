''''
For now just copy and paste to terminal whenever you need to perform this
actions
'''
import csv
import os

from django.conf import settings

from busstops.models import BusStop


proj_dir = settings.BASE_DIR
filename = os.path.join(os.path.dirname(proj_dir), 'busstops/scripts/new_busstops.csv')
FIELDNAMES = ('s/n', 'name', 'area', 'latitude', 'longitude', 'place_id')


def read_csv(filename):
    result = []
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=FIELDNAMES)
        for row in reader:
            result.append(row)
    return result


def write_csv_to_db(filename):
    csv_file = read_csv(filename)
    for index, row in enumerate(csv_file):
        BusStop.objects.create(
            name=row['name'],
            area=row['area'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            place_id=row['place_id']
        )
