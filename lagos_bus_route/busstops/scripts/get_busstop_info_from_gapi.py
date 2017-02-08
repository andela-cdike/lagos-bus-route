import csv
import random

import googlemaps


API_KEYS = [
    'AIzaSyCiL4EM_P-DXF1l5XHRxoPxMmDQ8vo7qQw',
    'AIzaSyBV8MTk96EawZ3OVLbx-6uMAwVeC2O3bUw',
    'AIzaSyCt7JdcEzFU14DcDEEY6edTZXoz0qbA8Ws',
    'AIzaSyAaXxWBCYV68QY_4vDrw-lUoYwAofSHKrY',
    'AIzaSyCQT_vYIpWxMzH8VBa8DBZtAF5Hr_PihIM',
    'AIzaSyDuxc_p7LNcAK7nkvo4eGC3zAqX3yidWS4',
    'AIzaSyB4hNuym8EKw345DFvbKzQSeH9i7d3DJSw',
]


def populate_csv_file_with_busstop_info():
    '''
    Fill a csv file with important information about busstops
    '''
    fieldnames = ('s/n', 'name', 'area', 'latitude', 'longitude', 'place_id')
    csv_file = read_csv('busstops.csv', fieldnames)
    for index, row in enumerate(csv_file, start=1):
        api_key = next(get_api_key())
        place_info = get_place_info_from_gapi(api_key, row)
        if not place_info:
            continue
        busstop_info = merge_dicts(row, place_info)
        write_to_file('new_busstops.csv', fieldnames, busstop_info, index)


def merge_dicts(*dict_args):
    '''
    Given any number of dictionaries, shallow copy and merge into a new dict
    precedence goes to key value pairs in latter dicts
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def get_api_key():
    '''
    A generator that returns an API key whenever it is called
    '''
    random.seed()
    while True:
        yield random.choice(API_KEYS)


def read_csv(filename, fieldnames):
    result = []
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        for row in reader:
            result.append(row)
    return result


def get_place_info_from_gapi(api_key, busstop_info):
    '''
    Get places information about busstops from google places API
    Args:
        api_key (string): google api key
        busstop_info (dict): {
            's/n',
            'name'
            'area'
        }
    '''
    gmaps = googlemaps.Client(api_key)
    address = '{name} bus stop {area}'.format(name=busstop_info['name'],
                                              area=busstop_info['area'])
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        geocode_result = {
            'latitude': geocode_result[0]['geometry']['location']['lat'],
            'longitude': geocode_result[0]['geometry']['location']['lng'],
            'place_id': geocode_result[0]['place_id']
        }
        return geocode_result
    report_error(busstop_info)
    return {}


def report_error(busstop_info):
    '''Write error to a file'''
    filename = 'error.csv'
    fieldnames = ('s/n', 'name', 'area')
    with open(filename, 'awb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({
            's/n': busstop_info['s/n'],
            'name': busstop_info['name'],
            'area': busstop_info['area']
        })


def write_to_file(filename, fieldnames, busstop_info, index):
    with open(filename, 'awb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if index == 0:
            writer.writeheader()
        writer.writerow({
            's/n': index,
            'name': busstop_info['name'],
            'area': busstop_info['area'],
            'latitude': busstop_info['latitude'],
            'longitude': busstop_info['longitude'],
            'place_id': busstop_info['place_id']
        })


if __name__ == '__main__':
    populate_csv_file_with_busstop_info()
