import factory

from busstops.models import BusStop
from routes.models import Route


class BusStopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BusStop

    name = factory.Sequence(lambda n: 'busstop_{0}'.format(n))
    area = factory.Sequence(lambda n: 'area_{0}'.format(n))
    latitude = factory.Sequence(lambda n: '6.9092390{0}'.format(n))
    longitude = factory.Sequence(lambda n: '3.9092390{0}'.format(n))
    place_id = factory.Sequence(lambda n: 'ChIJTQxdRDiMOxARY4IB{0}c'.format(n))


class RouteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Route

    busstop = factory.SubFactory(BusStopFactory)
    busstop_type = 'TR'
    route_id = 0
    node_position = 0
