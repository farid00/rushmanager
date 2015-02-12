# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brother',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('brother_name', models.CharField(max_length=200)),
                ('brother_year', models.IntegerField(default=1)),
                ('brother_years_in_fraternity', models.IntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rush',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rush_name', models.CharField(max_length=200)),
                ('rush_number', models.CharField(max_length=30)),
                ('rush_facebook_link', models.CharField(max_length=200)),
                ('rush_contacted_date', models.DateField(verbose_name=b'Date Contacted')),
                ('rush_email_address', models.CharField(max_length=100)),
                ('rush_rank', models.IntegerField(default=5)),
                ('rush_contact', models.ForeignKey(to='rushtracker.Brother')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]