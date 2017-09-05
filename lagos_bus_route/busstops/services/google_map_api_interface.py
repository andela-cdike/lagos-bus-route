import googlemaps


class GoogleMapApiInterface(object):
    """docstring for GoogleMapApiInterface
    Calls to the google map API should be made through this interface
    """

    def __init__(self):
        self.gmaps = googlemaps.Client(
            key='AIzaSyCt7JdcEzFU14DcDEEY6edTZXoz0qbA8Ws')

    def get_nearby_busstops(self, address=None, radius=800):
        '''
        Args:
            address (string) - address to locate busstops around
            radius (int) -- distance in meters in which to bias results
        Returns:
            a list of names of busstops close to the supplied address
            (distance determined by the radius argument)
        '''
        busstop_names = []
        nearby_places_result = {}
        location_coordinates = self.get_coordinates(address)
        if location_coordinates:
            # TODO: Rather than have fixed wide radius, this should be
            # incrementing from say 250m until busstops are returned
            # else, we could have a bunch of busstops returned for a particular route
            nearby_places_result = self.gmaps.places_nearby(
                location=location_coordinates,
                radius=radius,
                type='bus_station',
            )
        if nearby_places_result and nearby_places_result['status'] == 'OK':
            busstop_names = self.extract_busstop_names_from_api_response(
                nearby_places_result['results'])
        return busstop_names

    def extract_busstop_names_from_api_response(self, busstops):
        '''
        Extract the names of bus stops from a list containing bus stops and
        information about them.
        Args:
            busstops -- a list of busstops with associated information
        Returns:
            a list containing bus stop names
        '''
        busstop_names = []
        for busstop in busstops:
            busstop_names.append(busstop['name'])
        return busstop_names

    def get_coordinates(self, address):
        '''Return a dictionary of the longitude and latitude of
        the supplied address
        Args:
            address -- a sring representation of the address
        Assumptions:
            assumes the first returned location is the best match and returns
            that one.
        Returns:
            a dictonary rep of the coordinates
            e.g. {u'lat': 6.5039579, u'lng': 3.3514875}
            or an empty dictionary if google returned nothing
        '''
        geocode_result = self.gmaps.geocode(address)
        if geocode_result:
            return geocode_result[0]['geometry']['location']
        return {}
