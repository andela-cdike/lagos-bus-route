'''
A simple process is one that supplies the busstop
A complex/not so simple process is one that doesn't provide a specific
busstop and thus relies on the processor to get the best busstop based on
the supplied location. It should have an asterisk in front.

Note: this is mostly for the SMS app as the web app would suggest busstops in
the database as you type.
'''

from collections import namedtuple

from busstops.models import BusStop


class BusstopProcessor(object):

    # a location record consists of the busstop and an area
    locationRecord = namedtuple(
        'locationRecord', ['busstop_or_address', 'area'])

    def __init__(self, raw_location):
        self.raw_location = raw_location.lower().replace(', ', ',')
        self.check_type_of_process()

    def check_type_of_process(self):
        if self.raw_location[0] == '*':
            self.is_simple_process = False
        else:
            self.is_simple_process = True

    def process(self):
        '''Entry point of the class
        Args:
            name -- a string representing a raw_location
        Returns:
            a dictionary of the best match and other close matches
            that could be used in a separate query.
        '''
        location_record = self.format_location()
        location_records = self.reduce_location_to_busstops(location_record)
        busstops = self.get_busstop(location_records)
        result = self.prepare_result(busstops)
        return result

    def prepare_result(self, busstops):
        '''Format results as a dictionary with two keys:
            match -- the best match busstop to the supplied location
            others -- other matched busstops
        '''
        num_busstops = len(busstops)
        result = {'match': None, 'others': []}
        result['match'] = busstops[0] if num_busstops else None
        if len(busstops) > 1:
            result['others'].extend(busstops[1:])
        return result

    def format_location(self):
        '''
        Converts raw_location to location record
        '''
        if self.is_simple_process:
            location = self.raw_location.split(',')
        else:
            location = self.raw_location[1:].split(',')
        self.validate_raw_location(location)
        location_record = self.transform_to_location_record(location)
        return location_record

    def transform_to_location_record(self, location):
        '''
        Args:
            address - a list with:
                busstop or address in first index position; and
                area in the second index position
        Returns:
            a location_record
        '''
        return self.locationRecord(
            busstop_or_address=location[0],
            area=location[1]
        )

    def validate_raw_location(self, location):
        '''returns an empty string for the area parameter in the case
        that location doesn't include it
        '''
        if len(location) < 2:
            location.append('')
        return location

    def reduce_location_to_busstops(self, location_record):
        '''Reduce a location address to its busstop for complex processes
        Args:
            location_record
        Returns:
            a set of busstops
        '''
        if self.is_simple_process:
            return [location_record]
        location_records = []
        busstops = self.get_busstops_from_google_map_api(location_record)
        for busstop in busstops:
            location_records.append(
                self.transform_to_location_record(
                    [busstop, location_record.area]
                )
            )
        return location_records

    def get_busstops_from_google_map_api(self, location_record):
        '''
        100m radius
        Args:
            location_record
        Return:
            a list of busstops arranged in order of proximity to
            supplied location e.g. ['lawanson', 'ogunlana']
        '''
        return ['lawanson', 'ogunlana', 'otofina', 'bundafon']

    def get_busstop(self, location_records):
        '''Returns a list of BusStop objects'''
        busstops = []
        for record in location_records:
            res = BusStop.get_queryset(record.busstop_or_address, record.area)
            for busstop in res:
                busstops.append(busstop)
        return busstops
