from django.contrib import admin
from django.apps import apps

from routes.models import Route


@admin.register(Route)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('id', 'busstop', 'busstop_type',
                    'route_id', 'node_position')
    search_fields = ('busstop__name',)
