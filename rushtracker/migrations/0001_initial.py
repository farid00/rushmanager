# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rushperiod', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rush',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=200, verbose_name=b'First Name')),
                ('last_name', models.CharField(max_length=200, null=True, verbose_name=b'Last Name', blank=True)),
                ('phone_number', models.CharField(max_length=30, null=True, verbose_name=b'Phone Number', blank=True)),
                ('facebook_link', models.CharField(max_length=200, null=True, verbose_name=b'FaceBook Link', blank=True)),
                ('contacted_date', models.DateField(null=True, verbose_name=b'Date Contacted', blank=True)),
                ('email_address', models.EmailField(max_length=100, null=True, verbose_name=b'Email Address', blank=True)),
                ('rank', models.IntegerField(default=5, null=True, verbose_name=b'Rank', blank=True)),
                ('dorm', models.CharField(max_length=200, null=True, verbose_name=b'Dorm', blank=True)),
                ('picture', models.ImageField(null=True, upload_to=b'profile_picture', blank=True)),
                ('organization', models.ForeignKey(to='organization.Organization')),
                ('primary_contact', models.ForeignKey(related_name='primary_contact_set', verbose_name=b'Brotherhood Contact', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('rush_period', models.ManyToManyField(to='rushperiod.RushPeriod')),
                ('secondary_contact', models.ForeignKey(related_name='secondary_contact_set', verbose_name=b'Secondary Brotherhood Contact', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
