# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-11 16:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20161211_1643'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tournamentteam',
            unique_together=set([('name', 'tournament')]),
        ),
    ]
