# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os

from django.conf import settings
from django.db import IntegrityError, migrations


logger = logging.getLogger(__name__)


def forwards_func(apps, schema_editor):
    """Busstops were not loaded the first into production db initially
    since that wasn't populated via data migration initially.
    Therefore, development busstop table was dumped so it could be used
    to populate other environments
    """
    if os.getenv('ENVIRONMENT') == settings.PRODUCTION:
        BusStop = apps.get_model('busstops', 'BusStop')
        root_dir = os.path.dirname(os.path.dirname(settings.BASE_DIR))
        routes_json_filename = '{root_dir}/json_backups/busstops/24-11-17.json'.format(
            root_dir=root_dir)

        with open(routes_json_filename) as json_data:
            busstops = json.load(json_data)

        try:
            BusStop.objects.bulk_create(
                (BusStop(**busstop['fields']) for busstop in busstops))
        except IntegrityError as exc:
            logger.debug(dict(
                msg=(
                    "Skipping bulk create.... Some busstops already exist."
                    "Consider saving individually"),
                exception=exc
            ))


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('busstops', '0004_auto_20170225_1621'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
