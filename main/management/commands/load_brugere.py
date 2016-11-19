import json

from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from main.models import Profile


class Command(BaseCommand):
    help = 'Loads legacy users from a json file'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+', type=str)

    def handle(self, *args, **options):
        with open(options['file'][0], 'r') as f:
            users = json.load(f)
            for user in users:
                self.stdout.write('Adding user: {}'.format(user['brugernavn']))
                if user['klasse'] == 'Lærer':
                    user['klasse'] = 'teacher'
                try:
                    u = User.objects.create(username=user['brugernavn'], first_name=user['fullname'][:30],
                                            email=user['mail'],
                                            password='bcrypt$$2a' + user['new_kodeord'][3:])
                    p = Profile.objects.create(user=u, grade=user['klasse'])
                except IntegrityError:
                    pass
