from django.contrib import admin

from busstops.models import BusStop


@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'area', 'latitude', 'longitude', 'place_id')
    search_fields = ('name', 'area', 'place_id')
