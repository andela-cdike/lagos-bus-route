from __future__ import unicode_literals

from django.db import models

from busstops.models import Base


class Route(Base):
    '''
    This model represents a table that holds all the danfo routes in Lagos.
    Each route is identified by a route_id.

    Properties:
    busstop -- a relationship to the busstop record on the busstop model
    busstop_type -- distinguishes between terminal points and transit points
                    a mulitiple choice field
    route_id -- identifies and distinguishes different routes in the table
    '''
    TERMINAL = 'TE'
    TRANSIT = 'TR'
    BUSSTOP_TYPES = (
        (TERMINAL, 'Terminal'),
        (TRANSIT, 'Transit'),
    )
    busstop = models.ForeignKey('busstops.BusStop')
    busstop_type = models.CharField(
        max_length=2,
        choices=BUSSTOP_TYPES,
        default='TE'
    )
    route_id = models.IntegerField()

    def __str__(self):
        return '{0}, type-{1}, route {2}'.format(
            self.busstop.name, self.busstop_type, self.route_id)
