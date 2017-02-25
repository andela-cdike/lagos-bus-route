from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('busstops', '0002_auto_20170222_1432'),
    ]

    operations = [
        TrigramExtension(),
    ]
