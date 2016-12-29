import factory

from busstops.models import BusStop
from routes.models import Route


class BusStopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BusStop

    name = factory.Sequence(lambda n: 'busstop_{0}'.format(n))
    area = factory.Sequence(lambda n: 'area_{0}'.format(n))


class RouteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Route

    busstop = factory.SubFactory(BusStopFactory)
    busstop_type = 'TR'
    route_id = 0
    node_position = 0
