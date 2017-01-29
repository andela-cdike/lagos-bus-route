from __future__ import unicode_literals

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

    def __str__(self):
        return self.name