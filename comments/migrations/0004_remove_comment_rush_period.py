# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_auto_20150311_0017'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='rush_period',
        ),
    ]
