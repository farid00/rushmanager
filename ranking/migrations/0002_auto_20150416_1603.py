# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ranking', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ranking',
            name='ranking',
        ),
        migrations.AddField(
            model_name='ranking',
            name='rank',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
