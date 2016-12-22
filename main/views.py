import logging
from collections import defaultdict
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.timezone import now, utc
from django.shortcuts import render, redirect
from dal import autocomplete
from sorl.thumbnail import get_thumbnail

from main.models import get_next_lan, LanProfile, Profile, Tournament, TournamentTeam
from .forms import UserRegForm, ProfileRegForm, TilmeldForm, EditUserForm, EditProfileForm, TournamentTeamForm


# Actual pages

def index(request):
    """Front page"""
    return render(request, 'index.html', {'next_lan': get_next_lan()})


def info(request):
    """Information page"""
    return render(request, 'info.html', {'next_lan': get_next_lan()})


def tilmeld(request):
    """Tilmeldings page"""
    lan = get_next_lan()
    if lan is None:
        return redirect(reverse('index'))
    seats, count = lan.parse_seats()
    try:
        current = LanProfile.objects.get(lan=lan, profile=request.user.profile).seat
    except LanProfile.DoesNotExist:
        current = -1
    except AttributeError:
        current = 0
    count = (LanProfile.objects.filter(lan=lan).count(), count)
    if request.method == 'POST':
        form = TilmeldForm(request.POST, seats=seats, lan=lan, profile=request.user.profile)
        if form.is_valid() and lan.is_open() and count[0] < count[1]:
            created = form.save(profile=request.user.profile, lan=lan)
            if created:
                messages.add_message(request, messages.SUCCESS, "Du er nu tilmeldt LAN!")
            else:
                messages.add_message(request, messages.SUCCESS, "Tilmelding ændret!")
            return redirect(reverse("tilmeld"))
    else:
        if request.user.is_authenticated:
            profile = request.user.profile
        else:
            profile = None
        form = TilmeldForm(seats=seats, lan=lan,
                           profile=request.user.profile if request.user.is_authenticated else None)
    open_time = (lan.open - now()).total_seconds()
    return render(request, 'tilmeld.html', {'current': current, 'seats': seats, 'form': form, 'lan': lan,
                                            'opens_time': open_time, 'count': count, 'phone': settings.PAYMENT_PHONE})


def tilmeldlist(request):
    lan = get_next_lan()
    profiles = LanProfile.objects.filter(lan=lan)
    return render(request, 'tilmeldlist.html', {'profiles': profiles})


def register(request):
    """Registration page"""
    if request.method == 'POST':
        user_form = UserRegForm(request.POST)
        profile_form = ProfileRegForm(request.POST)
        user_form_valid = user_form.is_valid()
        profile_form_valid = profile_form.is_valid()
        if user_form_valid and profile_form_valid:
            user = user_form.save()
            prof = profile_form.save(commit=False)
            prof.user = user
            prof.save()
            login(request, user)
            return redirect(reverse('registered'))
    else:
        user_form = UserRegForm()
        profile_form = ProfileRegForm()

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})


def registered(request):
    """After registration page"""
    return render(request, 'registered.html')


def profile(request, username=None):
    """Profile view/edit page"""
    user_form, profile_form = None, None
    start_edit = False

    if username is None:
        if request.user.is_authenticated():
            username = request.user.username
        else:
            return redirect(reverse('needlogin'))

    try:
        prof = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        raise Http404
    try:
        if request.method == 'POST':
            if prof.id == request.user.profile.id:
                user_form = EditUserForm(request.POST, instance=request.user)
                profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
                if user_form.is_valid() and profile_form.is_valid():
                    user_form.save()
                    prof = profile_form.save()
                    messages.add_message(request, messages.SUCCESS, 'Profil opdateret!')
                    return redirect("profile", username=prof.user.username)
                else:
                    start_edit = True
        else:
            if prof.id == request.user.profile.id:
                user_form = EditUserForm(instance=request.user)
                profile_form = EditProfileForm(instance=request.user.profile)
    except AttributeError:
        pass

    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form,
                                            'profile': prof, 'start_edit': start_edit})


def tournaments(request):
    lan = get_next_lan()
    tournaments = Tournament.objects.filter(lan=lan).select_related('game')
    games = defaultdict(list)
    for t in tournaments:
        games[t.game].append(t)

    if request.user.is_authenticated:
        if request.method == 'POST':
            if 'frameld' in request.POST:
                try:
                    team = TournamentTeam.objects.get(id=int(request.POST['frameld']),
                                                      profiles__in=[request.user.profile])
                    messages.add_message(request, messages.SUCCESS,
                                         'Holdet {} er blevet frameldt turneringen'.format(team.name))
                    team.delete()
                except (TournamentTeam.DoesNotExist, ValueError):
                    messages.add_message(request, messages.ERROR,
                                         'Der opstod en fejl. Prøv igen senere, eller kontakt LanCrew.')

        teams = TournamentTeam.objects.filter(tournament__lan=lan, profiles__in=[request.user.profile])
    else:
        teams = None
    return render(request, 'tournaments.html', {'games': dict(games), 'teams': teams})


def tournament(request, game, lan_id, name):
    t = Tournament.objects.get(game__name=game, lan__id=lan_id, name=name)
    teams = TournamentTeam.objects.filter(tournament=t)
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TournamentTeamForm(request.POST, tournament=t, profile=request.user.profile)
            if form.is_valid() and t.open:
                team = form.save()
                messages.add_message(request, messages.SUCCESS, 'Hold tilmeldt successfuldt!')
                send_tournament_mails(request, team)
                form = TournamentTeamForm(tournament=t, profile=request.user.profile)
        else:
            form = TournamentTeamForm(tournament=t, profile=request.user.profile)
    else:
        form = None
    return render(request, 'tournament.html', {'tournament': t, 'teams': teams, 'form': form})


def send_tournament_mails(request, team):
    site = 'https://htxaarhuslan.dk'  # Naughty naugthy hard code
    for p in team.profiles.all():
        p.user.email_user(
            '{} tilmeldt til {} på HTXAarhusLAN.dk'.format(team.name, team.tournament.name),
            render_to_string('tournament_mail.html', {'team': team, 'profile': p, 'site': site})
        )


def legacy(request):
    return render(request, 'legacy.html')


def needlogin(request):
    referrer = request.GET.get('next', None)
    if request.user.is_authenticated():
        if referrer is not None:
            return redirect(referrer)
        else:
            return redirect(reverse('index'))
    return render(request, 'needlogin.html')


def policy(request):
    return render(request, 'policy.html')


# Meta pages

def login_view(request):
    """Post url for login form, always redirects the user back unless legacy."""
    referrer = request.GET.get('next', reverse("index"))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            is_legacy = (user.date_joined < datetime(2016, 11, 22).replace(tzinfo=utc) and not user.last_login)
            login(request, user)
            if is_legacy:
                return redirect(reverse('legacy'))
        else:
            messages.add_message(request, messages.ERROR, "Fejl i brugernavn eller kodeord")
    return redirect(referrer)


def logout_view(request):
    """Logout and redirect."""
    logout(request)
    referrer = request.GET.get('next', reverse("index"))
    return redirect(referrer)


def frameld(request):
    """Framelds a user"""
    lan = get_next_lan()
    success = False
    if request.method == 'POST':
        try:
            current = LanProfile.objects.get(lan=lan, profile=request.user.profile)
            success = current.delete(keep_parents=True)
            try:
                teams = TournamentTeam.objects.filter(tournament__lan=lan,
                                                      profiles__in=[request.user.profile])
                teams.delete()
            except (TournamentTeam.DoesNotExist, ValueError):
                pass
        except LanProfile.DoesNotExist:
            pass
        except AttributeError:
            pass
    if success:
        messages.add_message(request, messages.SUCCESS, "Du er nu frameldt LAN!")
    else:
        messages.add_message(request, messages.ERROR, "Der opstod en fejl med din framelding. Prøv igen senere.")
    return redirect(reverse("tilmeld"))


class ProfileAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return False

        lan = get_next_lan()
        qs = Profile.objects.filter(lanprofile__lan=lan)

        exclude = [int(x) for x in self.forwarded.values() if x] + [self.request.user.profile.id, ]
        qs = qs.exclude(pk__in=exclude)

        if self.q:
            qs = qs.filter(Q(user__username__icontains=self.q) |
                           Q(user__first_name__icontains=self.q) |
                           Q(grade__icontains=self.q))

        return qs

    def get_result_label(self, item):
        html = ''
        if item.photo:
            im = get_thumbnail(item.photo, '60x60', crop='center')
            if im:
                html += '<img src="{}" />'.format(im.url)
        html += '<span>{}</span><br><span>{}<span>&nbsp;({})</span></span>'.format(item.user.first_name,
                                                                                   item.user.username,
                                                                                   item.get_grade_display())
        return html
