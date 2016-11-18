from collections import Counter

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

# noinspection SpellCheckingInspection

grades = {
    'xa': {
        13: [],
        14: ['a', 'b', 'c', 'd', 'r', 'j'],
        15: ['a', 'b', 'c', 'd', 'r', 'j'],
        16: ['a', 'b', 'c', 'd', 'r', 'j']
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
    photo = models.ImageField(upload_to=profile_picture_path, blank=True, verbose_name='billede')
    bio = models.TextField(blank=True)
    grade = models.CharField(verbose_name='klasse', max_length=32, choices=GRADES, default='none')

    def __str__(self):
        return '{} ({})'.format(self.user.username, self.user.first_name)


class Lan(models.Model):
    class Meta:
        verbose_name = 'LAN'
        verbose_name_plural = 'LAN'

    start = models.DateTimeField()
    end = models.DateTimeField()
    open = models.DateTimeField()
    name = models.CharField(max_length=255)
    profiles = models.ManyToManyField(Profile, through='LanProfile')
    seats = models.TextField()
    schedule = models.TextField()
    blurb = models.TextField()

    def __str__(self):
        return '{} ({})'.format(self.name, self.start.strftime('%d. %b. %Y'))

    def is_open(self):
        return self.open <= now()

    def parse_seats(self):
        parsed = []
        tables = Counter()
        users = self.profiles.all().select_related()
        for row in self.seats.splitlines():
            parsed.append([])
            for s in row:
                if s != '-':
                    tables[s] += 1
                    seat = '{}{:02d}'.format(s, tables[s])
                    try:
                        user = users.get(lanprofile__seat=seat, lanprofile__lan=self)
                        parsed[-1].append((seat, user))
                    except Profile.DoesNotExist:
                        parsed[-1].append((seat, None))
                else:
                    parsed[-1].append((None, None))
        return parsed, sum(tables.values())


class LanProfile(models.Model):
    class Meta:
        verbose_name = 'tilmelding'
        verbose_name_plural = 'tilmeldinger'
        unique_together = (('lan', 'seat'), ('lan', 'profile'))

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    lan = models.ForeignKey(Lan, on_delete=models.CASCADE)
    seat = models.CharField(max_length=8, blank=True, null=True)

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
