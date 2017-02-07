# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-07 18:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20170207_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodorder',
            name='lanprofile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.LanProfile', verbose_name='tilmelding'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='grade',
            field=models.CharField(choices=[('16xvu', '16xvu'), ('16xvx', '16xvx'), ('16xvy', '16xvy'), ('16xvz', '16xvz'), ('13xv', '13xv'), ('14xvu', '14xvu'), ('14xvx', '14xvx'), ('14xvy', '14xvy'), ('14xvz', '14xvz'), ('15xvu', '15xvu'), ('15xvt', '15xvt'), ('15xvx', '15xvx'), ('15xvz', '15xvz'), ('16xsi', '16xsi'), ('16xsm', '16xsm'), ('16xsk', '16xsk'), ('13xs', '13xs'), ('14xsi', '14xsi'), ('14xsm', '14xsm'), ('15xsi', '15xsi'), ('15xsm', '15xsm'), ('16xaa', '16xaa'), ('16xab', '16xab'), ('16xac', '16xac'), ('16xad', '16xad'), ('16xae', '16xae'), ('16xaf', '16xaf'), ('16xaj', '16xaj'), ('16xap', '16xap'), ('16xar', '16xar'), ('13xa', '13xa'), ('14xaa', '14xaa'), ('14xab', '14xab'), ('14xad', '14xad'), ('14xae', '14xae'), ('14xaj', '14xaj'), ('14xap', '14xap'), ('14xaq', '14xaq'), ('14xar', '14xar'), ('15xaa', '15xaa'), ('15xab', '15xab'), ('15xac', '15xac'), ('15xad', '15xad'), ('15xae', '15xae'), ('15xaj', '15xaj'), ('15xap', '15xap'), ('15xar', '15xar'), ('teacher', 'Lærer'), ('none', 'Ukendt')], default='none', max_length=32, verbose_name='klasse'),
        ),
    ]
