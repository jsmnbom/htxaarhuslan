# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-15 20:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20161211_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='challonge_id',
            field=models.IntegerField(help_text='Udfyles selv, når du trykker gem.', null=True, verbose_name='Challonge id'),
        ),
        migrations.AddField(
            model_name='tournament',
            name='extra_challonge',
            field=models.TextField(help_text='Advannceret: ekstra data til challonge API. Angives i JSON format.', null=True, verbose_name='Extra challonge data'),
        ),
        migrations.AddField(
            model_name='tournament',
            name='live',
            field=models.BooleanField(default=False, help_text='Er turneringen i gang? (viser live opdates på siden hvis ja)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tournament',
            name='open',
            field=models.BooleanField(default=True, help_text='Er der åbent for tilmelding? Hvis nej bliver turneringen ikke vist på siden.Bemærk at LanCrew medlemmer dog altid kan tilmelde sig.', verbose_name='Tilmelding mulig?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tournamentteam',
            name='challonge_id',
            field=models.IntegerField(default=0, help_text='Udfyldes selv, når du trykker gem.', verbose_name='Challonge id'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tournament',
            name='team_size',
            field=models.IntegerField(verbose_name='Holdstørrelse'),
        ),
    ]
