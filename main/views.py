from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect
from dal import autocomplete

from main.models import get_next_lan, LanProfile, Profile
from .forms import UserRegForm, ProfileRegForm, TilmeldForm, EditUserForm, EditProfileForm


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
        form = TilmeldForm(request.POST, seats=seats)
        if form.is_valid() and lan.is_open() and count[0] < count[1]:
            created = form.save(profile=request.user.profile, lan=lan)
            if created:
                messages.add_message(request, messages.SUCCESS, "Du er nu tilmeldt LAN!")
            else:
                messages.add_message(request, messages.SUCCESS, "Tilmelding ændret!")
            return redirect(reverse("tilmeld"))
    else:
        form = TilmeldForm(seats=seats)
    return render(request, 'tilmeld.html', {'current': current, 'seats': seats, 'form': form, 'open': lan.is_open(),
                                            'opens_time': int(lan.open.timestamp() * 1000), 'count': count})


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


def profile(request, username):
    """Profile view/edit page"""
    user_form, profile_form = None, None
    start_edit = False
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


def tournament(request):
    return render(request, 'tournament.html')


# Meta pages

def login_view(request):
    """Post url for login form, always redirects the user back."""
    username = request.POST.get('username')
    password = request.POST.get('password')
    referrer = request.GET.get('next', reverse("index"))
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
    else:
        messages.add_message(request, messages.ERROR, "Fejl i brugernavn eller kodeord")
    return redirect(referrer)


def logout_view(request):
    """Logout and redirect."""
    logout(request)
    referrer = request.GET.get('next', reverse("index"))
    return redirect(referrer)


def frameld(request):
    """Framelds a user

    (This might need to be a POST so we can csrf secure it)
    """
    lan = get_next_lan()
    try:
        current = LanProfile.objects.get(lan=lan, profile=request.user.profile)
        current.delete(keep_parents=True)
        messages.add_message(request, messages.INFO, "Du er nu frameldt LAN!")
    except LanProfile.DoesNotExist:
        pass
    except AttributeError:
        pass
    return redirect(reverse("tilmeld"))


class ProfileAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_staff:
            return Profile.objects.none()

        qs = Profile.objects.all()

        if self.q:
            qs = qs.filter(Q(user__username__icontains=self.q) | Q(user__first_name__icontains=self.q))

        return qs
