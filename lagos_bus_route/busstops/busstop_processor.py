'''
A simple process is one that supplies the busstop
A complex/not so simple process is one that doesn't provide a specific
the supplied location. It should have an asterisk in front.
busstop and thus relies on the processor to get the best busstop based on

Note: this is mostly for the SMS/messenger (basically any text based) app as
the web app would suggest busstops in the database as you type.
'''

import functools
import logging
import operator
from collections import namedtuple

import jellyfish

from busstops.models import BusStop
from busstops.services.google_map_api_interface import GoogleMapApiInterface


logger = logging.getLogger(__name__)


class BusstopProcessor(object):
    """Initialize with a string of the busstop and aread
    samples:
    -- lawanson, surulere
    -- *ajao, surulere
    -- *ajao road
    """

    # a location record consists of the busstop and an area
    locationRecord = namedtuple(
        'locationRecord', ['busstop_or_address', 'area', 'place_id'])

    def __init__(self, raw_location):
        self.raw_location = raw_location.lower().replace(', ', ',')
        self.update_process_type()

    def update_process_type(self):
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
        logger.info(dict(
            msg='Busstop processor result {0}'.format(self.raw_location),
            result=result, type='busstop_processor_process'
        ))
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
        return self.locationRecord(*location, place_id=None)

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
                self.locationRecord(
                    busstop.name, location_record.area, busstop.place_id)
            )
        return location_records

    def get_busstops_from_google_map_api(self, location_record):
        '''
        100m radius
        Args:
            location_record
        Return:
            a list of busstops
        '''
        gmap_api_interface = GoogleMapApiInterface()
        address = '{0} {1}'.format(
            location_record.busstop_or_address,
            location_record.area if location_record.area else 'lagos'
        )
        busstops = gmap_api_interface.get_nearby_busstops(address)

        # only sort by jaro distance when there is a jellyfish rating comparison match
        # between address and any of the busstops
        mrc_with_address = functools.partial(
            jellyfish.match_rating_comparison, unicode(address))
        if len(busstops) > 1 and any(mrc_with_address(busstop.name) for busstop in busstops):
            busstops = self.sort_gmap_api_result_by_jaro_distance(
                location_record, busstops)
            logger.info(dict(
                msg='Sorted the following bus stops by jaro distance',
                busstops=busstops
            ))
        return busstops

    @staticmethod
    def sort_gmap_api_result_by_jaro_distance(location_record, busstops):
        """
        Arrange busstops by jaro_distance to the original busstop
        passed in so the most similar becomes the first match

        :param location_record: a locationRecord object holding the information
                                of the location searched
        :param busstops: a list of BusStopPayload items, gotten from google map API interface
        """
        jd_with_busstop = functools.partial(
            jellyfish.jaro_distance, location_record.busstop_or_address)
        busstops_by_jaro_distance = [
            (busstop, jd_with_busstop(busstop.name)) for busstop in busstops]

        return [
            busstop[0] for busstop in sorted(
                busstops_by_jaro_distance,
                key=operator.itemgetter(1),
                reverse=True
            )
        ]

    def get_busstop(self, location_records):
        '''Returns a list of BusStop objects'''
        busstops = []
        for record in location_records:
            if record.place_id:
                res = BusStop.get_by_place_id(record.place_id)
            else:
                res = BusStop.get_queryset(
                    record.busstop_or_address, record.area)
            for busstop in res:
                busstops.append(busstop)
        return busstops
