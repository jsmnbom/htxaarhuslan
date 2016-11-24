# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-05 21:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20161105_1236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lan',
            options={'verbose_name': 'LAN', 'verbose_name_plural': 'LAN'},
        ),
        migrations.AlterModelOptions(
            name='lanprofile',
            options={'verbose_name': 'tilmelding', 'verbose_name_plural': 'tilmeldinger'},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'profil', 'verbose_name_plural': 'profiler'},
        ),
        migrations.AlterUniqueTogether(
            name='lanprofile',
            unique_together=set([('lan', 'seat')]),
        ),
    ]