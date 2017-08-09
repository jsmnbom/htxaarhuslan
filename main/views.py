from collections import defaultdict
from datetime import datetime

from dal import autocomplete
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.timezone import now, utc
from sorl.thumbnail import get_thumbnail

from main.models import get_next_lan, LanProfile, Profile, Tournament, TournamentTeam, Event, FoodOrder
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
        form = TilmeldForm(seats=seats, lan=lan,
                           profile=request.user.profile if request.user.is_authenticated else None)

    open_time = (lan.open - now()).total_seconds()
    return render(request, 'tilmeld.html', {'current': current, 'seats': seats, 'form': form, 'lan': lan,
                                            'opens_time': open_time, 'count': count})


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
                                            'profile': prof, 'start_edit': start_edit, 'lan': get_next_lan()})


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
                return redirect(reverse('tournaments'))

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
                return redirect(reverse('tournament', kwargs={'game': game, 'lan_id': lan_id, 'name': name}))
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


def food(request):
    orders = []
    lan = get_next_lan()
    show = lan is not None and lan.is_open() and lan.food_open and request.user.is_authenticated()
    if request.user.is_authenticated():
        try:
            lp = LanProfile.objects.get(lan=lan, profile=request.user.profile)

            if request.method == 'POST':
                try:
                    keys = ['category', 'product', 'part1', 'part2', 'part3', 'acc1', 'acc2', 'acc3']
                    values = []
                    for key in keys:
                        value = request.POST.get(key)
                        if value:
                            values.append(value)
                    text = ' - '.join(values)
                    FoodOrder.objects.create(time=now(), lanprofile=lp, order=text,
                                             price=int(request.POST.get('price')))
                    messages.add_message(request, messages.SUCCESS,
                                         'Din bestilling er modtaget. Du kan nu betale herover.')
                    return redirect(reverse('food'))
                except KeyError:
                    pass

            orders = FoodOrder.objects.filter(lanprofile=lp)

        except LanProfile.DoesNotExist:
            show = False
    return render(request, 'food.html', {'lan': lan, 'show': show, 'orders': orders})


def event(request, event_id):
    return render(request, 'event.html', {'event': Event.objects.get(id=event_id)})


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

        try:
            exclude = [int(x) for x in self.forwarded.values() if x] + [self.request.user.profile.id, ]
            qs = qs.exclude(pk__in=exclude)
        except ValueError:  # It's a non lan user (therefore a str not int)
            pass

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


def calendar(request, feed_name):
    lan = get_next_lan()
    events = []
    if feed_name == 'tournament':
        ts = Tournament.objects.filter(lan=lan, start__isnull=False)
    elif feed_name == 'misc':
        ts = Event.objects.filter(lan=lan, start__isnull=False)
    else:
        raise Http404
    for t in ts:
        url = ''
        if isinstance(t, Tournament):
            if not (t.live or t.open):
                continue
            url = t.get_absolute_url()
        elif isinstance(t, Event):
            url = t.url
            if (url == '' or url is None) and (t.text != '' and t.text is not None):
                url = t.get_absolute_url()
        evt = {
            'title': '{}'.format(t.name),
            'start': t.start.isoformat(),
            'id': t.pk,
        }
        if url:
            evt['url'] = url
        if t.end:
            evt['end'] = t.end.isoformat()
        events.append(evt)
    return JsonResponse(events, safe=False)


def send_payment_request(request):
    pass
