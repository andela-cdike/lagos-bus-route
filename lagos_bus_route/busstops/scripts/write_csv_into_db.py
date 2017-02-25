from busstops.models import BusStop
from busstops.scripts.get_busstop_info_from_gapi import read_csv


def write_csv_to_db():
    filename = 'new_busstops.csv'
    csv_file = read_csv(filename)
    for index, row in enumerate(csv_file):
        BusStop.objects.create(
            name=row['name'],
            area=row['area'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            place_id=row['place_id']
        )


if __name__ == '__main__':
    write_csv_to_db()
