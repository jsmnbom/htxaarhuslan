import json
from collections import Counter
from collections import defaultdict

import challonge
from django import forms
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from sorl.thumbnail import ImageField

from main.storage import OverwriteStorage

grades = {
    'xa': {
        13: [],
        14: ['a', 'b', 'd', 'e', 'j', 'p', 'q', 'r'],
        15: ['a', 'b', 'c', 'd', 'e', 'j', 'p', 'r'],
        16: ['a', 'b', 'c', 'd', 'e', 'f', 'j', 'p', 'r']
    }
}

GRADES = ()
for school, years in grades.items():
    for year, classes in years.items():
        for class_ in classes:
            GRADES += (('{}{}{}'.format(year, school, class_),) * 2,)
        if not classes:
            GRADES += (('{}{}'.format(year, school),) * 2,)

GRADES += (('teacher', 'Lærer'),)

PAYTYPES = (
    ('mp', 'MobilePay'),
    ('cash', 'Kontant')
)


def profile_picture_path(instance, orig):
    ext = orig.split('.')[-1]
    filename = 'profile/{}.{}'.format(instance.pk, ext)
    return filename


class Profile(models.Model):
    class Meta:
        verbose_name = 'profil'
        verbose_name_plural = 'profiler'

    GRADES = GRADES + (('none', 'Ukendt'),)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = ImageField(upload_to=profile_picture_path, storage=OverwriteStorage(), blank=True,
                       verbose_name='billede')
    bio = models.TextField(blank=True)
    grade = models.CharField(verbose_name='klasse', max_length=32, choices=GRADES, default='none')

    def __str__(self):
        return '{} ({})'.format(self.user.username, self.user.first_name)


class StrippedMultipleChoiceFieldField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.pop('max_length')
        kwargs.pop('base_field')
        super().__init__(*args, **kwargs)


class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.

    Uses Django 1.9's postgres ArrayField
    and a MultipleChoiceField for its formfield.

    Usage:

        choices = ChoiceArrayField(models.CharField(max_length=...,
                                                    choices=(...,)),
                                   default=[...])
    """

    def formfield(self, **kwargs):
        defaults = {
            'form_class': StrippedMultipleChoiceFieldField,
            'base_field': self.base_field.formfield(),
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super().formfield(**defaults)


class Lan(models.Model):
    class Meta:
        verbose_name = 'LAN'
        verbose_name_plural = 'LAN'

    start = models.DateTimeField(verbose_name='start')
    end = models.DateTimeField(verbose_name='slut')
    open = models.DateTimeField(verbose_name='tildmelding åbner')
    name = models.CharField(max_length=255, verbose_name='navn')
    profiles = models.ManyToManyField(Profile, through='LanProfile')
    seats = models.TextField(verbose_name='pladser')
    schedule = models.TextField(verbose_name='tidsplan', null=True)
    blurb = models.TextField(verbose_name='blurb',
                             help_text='Teksten, specifikt til dette lan, der bliver vist på forsiden.<br>'
                                       'Husk at wrappe tekst i &lt;p> tags!')
    paytypes = ChoiceArrayField(models.CharField(max_length=127, choices=PAYTYPES), verbose_name='betalingstyper',
                                null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='pris', null=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.start.strftime('%d. %b. %Y'))

    def is_open(self):
        return self.open <= now()

    is_open.short_description = 'Tilmelding åben?'

    def parse_seats(self):
        parsed = []
        tables = Counter()
        users = self.profiles.filter(lan=self).select_related()
        for row in self.seats.splitlines():
            parsed.append([])
            for s in row:
                if s != '-':
                    tables[s] += 1
                    seat = '{}{:02d}'.format(s, tables[s])
                    try:
                        user = users.get(lanprofile__seat=seat, lan=self)
                        parsed[-1].append((seat, user))
                    except Profile.DoesNotExist:
                        parsed[-1].append((seat, None))
                else:
                    parsed[-1].append((None, None))
        return parsed, sum(tables.values())

    def seats_count(self):
        return self.parse_seats()[1]

    seats_count.short_description = 'Antal pladser'


class LanProfile(models.Model):
    class Meta:
        verbose_name = 'tilmelding'
        verbose_name_plural = 'tilmeldinger'
        unique_together = (('lan', 'seat'), ('lan', 'profile'))

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='profil')
    lan = models.ForeignKey(Lan, on_delete=models.CASCADE, verbose_name='lan')
    seat = models.CharField(max_length=8, blank=True, null=True, verbose_name='plads')
    paytype = models.CharField(max_length=255, null=True, blank=True, verbose_name='betalingstype', choices=PAYTYPES)
    paid = models.NullBooleanField(verbose_name='betalt?')

    def __str__(self):
        return self.profile.user.username + '@' + self.lan.name

    def save(self, *args, **kwargs):
        if not self.seat:
            self.seat = None
        super().save(*args, **kwargs)


def get_next_lan():
    lans = Lan.objects.filter(end__gte=now()).order_by('end')
    if len(lans) > 0:
        return lans[0]
    else:
        return None


class Game(models.Model):
    class Meta:
        verbose_name = 'spil'
        verbose_name_plural = 'spil'

    name = models.CharField(max_length=255, verbose_name='navn')
    description = models.TextField(verbose_name='beskrivelse')
    image = ImageField(upload_to='games/', storage=OverwriteStorage(), blank=True,
                       verbose_name='billede')

    def __str__(self):
        return self.name


class Tournament(models.Model):
    class Meta:
        verbose_name = 'turnering'
        verbose_name_plural = 'turneringer'

    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name='spil')
    lan = models.ForeignKey(Lan, on_delete=models.CASCADE, verbose_name='lan')
    name = models.CharField(max_length=255, verbose_name='navn')
    description = models.TextField(verbose_name='beskrivelse')
    team_size = models.IntegerField(verbose_name='Holdstørrelse')
    challonge_id = models.IntegerField(verbose_name='Challonge id', help_text="Udfyles selv, når du trykker gem.",
                                       null=True, blank=True)
    extra_challonge = models.TextField(null=True, verbose_name='Extra challonge data', blank=True,
                                       help_text='Advannceret: ekstra data til challonge API. Angives i JSON format.')
    live = models.BooleanField(help_text='Er turneringen i gang? (viser live opdates på siden hvis ja)')
    open = models.BooleanField(verbose_name='Tilmelding mulig?',
                               help_text='Er der åbent for tilmelding? Hvis nej bliver turneringen ikke vist på siden.'
                                         'Bemærk at LanCrew medlemmer dog altid kan tilmelde sig.')

    def __str__(self):
        return self.name

    def get_challonge_url(self):
        return '{}_{}_{}'.format('htxaarhuslan', self.lan.id, self.id)


@receiver(post_save, sender=Tournament, dispatch_uid='create_challonge')
def create_challonge(sender, instance, **kwargs):
    created = kwargs.get('created', False)
    if created:
        params = {
            'description': instance.description
        }
        if instance.extra_challonge:
            params.update(json.loads(instance.extra_challonge))
        tournament = challonge.tournaments.create(
            '{} – {} – {}'.format('HTXAarhusLAN', instance.lan.name, instance.name),
            instance.get_challonge_url(),
            params.get('tournament_type', 'single elimination'), **params)
        instance.challonge_id = tournament['id']
        instance.save()
    elif instance.challonge_id:
        url_params = {
            'game': instance.game.name,
            'lan_id': instance.lan.id,
            'name': instance.name
        }
        params = {
            'description': '{}<br><br>Tilmeld dig på: '
                           '<a href="https://htxaarhuslan.dk{}" target="_blank">{}</a>'.format(instance.description,
                                                                        reverse('tournament', kwargs=url_params),
                                                                        'HTXAarhuslan.dk'),
            'name': '{} – {} – {}'.format('HTXAarhusLAN', instance.lan.name, instance.name),
            'url': instance.get_challonge_url()
        }
        if instance.extra_challonge:
            params.update(json.loads(instance.extra_challonge))
        challonge.tournaments.update(instance.challonge_id, **params)


@receiver(post_delete, sender=Tournament, dispatch_uid='delete_challonge')
def delete_challonge(sender, instance, **kwargs):
    challonge.tournaments.destroy(instance.challonge_id)


class TournamentTeam(models.Model):
    class Meta:
        verbose_name = 'hold'
        verbose_name_plural = 'hold'
        unique_together = (('name', 'tournament'),)

    profiles = models.ManyToManyField(Profile, verbose_name='medlemmer')
    name = models.CharField(max_length=255, verbose_name='holdnavn')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    challonge_id = models.IntegerField(verbose_name='Challonge id', help_text='Udfyldes selv, når du trykker gem.',
                                       null=True, blank=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=TournamentTeam, dispatch_uid='create_challonge_team')
def create_challonge_team(sender, instance, **kwargs):
    created = kwargs.get('created', False)
    if created:
        participant = challonge.participants.create(instance.tournament.challonge_id,
                                                    instance.name,
                                                    misc=instance.id)
        instance.challonge_id = participant['id']
        instance.save()


@receiver(post_delete, sender=TournamentTeam, dispatch_uid='delete_challonge_team')
def delete_challonge_team(sender, instance, **kwargs):
    challonge.participants.destroy(instance.tournament.challonge_id, instance.challonge_id)
