# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-05 23:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20161105_2257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='grade',
            field=models.CharField(choices=[('16xaa', '16xaa'), ('16xab', '16xab'), ('16xac', '16xac'), ('16xad', '16xad'), ('16xar', '16xar'), ('16xaj', '16xaj'), ('14xaa', '14xaa'), ('14xab', '14xab'), ('14xac', '14xac'), ('14xad', '14xad'), ('14xar', '14xar'), ('14xaj', '14xaj'), ('15xaa', '15xaa'), ('15xab', '15xab'), ('15xac', '15xac'), ('15xad', '15xad'), ('15xar', '15xar'), ('15xaj', '15xaj'), ('teacher', 'Lærer'), ('none', 'Ukendt')], default='none', max_length=32, verbose_name='klasse'),
        ),
    ]
