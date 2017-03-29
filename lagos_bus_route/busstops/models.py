from __future__ import unicode_literals

from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class Base(models.Model):
    """
    Common fields are abstracted here
    """
    date_created = models.DateField(auto_now_add=True)
    date_last_modified = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class BusStop(Base):
    '''Represents a busstop'''

    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=22, decimal_places=20)
    longitude = models.DecimalField(max_digits=22, decimal_places=20)
    place_id = models.CharField(max_length=27, unique=True)

    class Meta:
        unique_together = (('latitude', 'longitude'),)

    def __str__(self):
        return self.name

    @staticmethod
    def get_queryset(busstop_name, busstop_area):
        queryset = BusStop.objects.annotate(similarity=TrigramSimilarity(
            'name', busstop_name),).filter(similarity__gt=0.5)
        if busstop_area:
            queryset = queryset.annotate(similarity=TrigramSimilarity(
                'area', busstop_area),).filter(similarity__gt=0.5)
        return queryset
