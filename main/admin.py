from collections import Counter
from pathlib import Path

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sorl.thumbnail.admin import AdminImageMixin

from main.forms import AdminLanProfileForm, AdminProfileForm
from .models import Profile, Lan, LanProfile, Tournament, Game, TournamentTeam, Event, get_next_lan, FoodOrder

admin.site.unregister(User)


# Allows us to have a default filter
class LanFilter(SimpleListFilter):
    title = 'lan'
    parameter_name = 'lan'

    def lookups(self, request, model_admin):
        return [(str(lan.pk), str(lan)) for lan in Lan.objects.all().order_by('-end')] + [('all', 'Vis alle')]

    def queryset(self, request, queryset):
        value = self.value()
        if value and not value == 'all':
            if queryset.model == TournamentTeam:
                return queryset.filter(tournament__lan_id=value)
            elif queryset.model == FoodOrder:
                return queryset.filter(lanprofile__lan_id=value)
            else:
                return queryset.filter(lan_id=value)
        return queryset

    def value(self):
        # What would the value have been?
        value = super().value()
        if value is None:
            lan = get_next_lan()
            if lan:
                value = lan.pk
        return str(value)


@admin.register(LanProfile)
class LanProfileAdmin(admin.ModelAdmin):
    list_filter = (LanFilter, 'paytype', 'paid', 'profile__grade', 'profile__user__groups')
    list_display = ('profile', 'lan', 'seat', 'get_paytype', 'paid')
    search_fields = ('profile__user__first_name', 'profile__user__username', 'seat')
    form = AdminLanProfileForm

    def get_paytype(self, obj):
        return obj.get_paytype_display()

    get_paytype.short_description = LanProfile._meta.get_field('paytype').verbose_name

    actions = ['paid', 'not_paid']

    def paid(self, request, queryset):
        queryset.update(paid=True)

    paid.short_description = "Makér som betalt."

    def not_paid(self, request, queryset):
        queryset.update(paid=False)

    not_paid.short_description = mark_safe(mark_safe("Markér som ikke betalt."))


class ProfileInline(AdminImageMixin, admin.StackedInline):
    model = Profile
    form = AdminProfileForm


@admin.register(User)
class MyUserAdmin(UserAdmin):
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return self.readonly_fields + ('is_staff', 'is_superuser',
                                       'groups', 'user_permissions')

    list_display = ('username', 'email', 'first_name', 'get_grade', 'is_staff')

    def get_grade(self, user):
        return user.profile.grade

    get_grade.short_description = 'Klasse'

    inlines = [
        ProfileInline
    ]

    list_filter = UserAdmin.list_filter + ('profile__grade',)


@admin.register(Lan)
class LanAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'seats_count', 'is_open')
    # form = AdminLanForm

    fieldsets = (
        ('Tider', {
            'fields': (('start', 'end'), 'open', 'show_calendar')
        }),
        ('Pladser', {
            'fields': ('seats',)
        }),
        ('Tekst', {
            'fields': ('name', 'schedule', 'blurb')
        }),
        ('Betaling', {
            'fields': ('paytypes', 'price')
        }),
        ('Madbestilling', {
            'fields': ('food_open', 'food_phone')
        }),
    )

    def get_changeform_initial_data(self, request):
        try:
            prev_lan = Lan.objects.filter(start__lt=now()).order_by("-start")[0]
            return model_to_dict(prev_lan, ['blurb', 'seats', 'schedule'])
        except (Lan.DoesNotExist, AttributeError, IndexError):
            return {}


class TournamentTeamInline(admin.TabularInline):
    model = TournamentTeam
    show_change_link = True

    fields = ('name',)  # If we show profiles too it slows down the SQL


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_filter = (LanFilter, 'game')
    list_display = ('name', 'game', 'lan', 'challonge_link', 'get_teams_count', 'live', 'open')
    search_fields = ('name', 'game', 'lan')

    inlines = [
        TournamentTeamInline
    ]

    def get_teams_count(self, tournament):
        return tournament.tournamentteam_set.count()

    get_teams_count.short_description = 'Antal hold'

    def challonge_link(self, tournament):
        return '<a href="http://challonge.com/{0}" target="_blank">{0}</a>'.format(tournament.get_challonge_url())

    challonge_link.allow_tags = True
    challonge_link.short_description = 'Challonge'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_filter = (LanFilter,)
    list_display = ('name', 'lan', 'start', 'end')
    search_fields = ('name', 'description')


@admin.register(TournamentTeam)
class TournamentTeamAdmin(admin.ModelAdmin):
    list_filter = (LanFilter, 'tournament__game', 'tournament')
    list_display = ('name', 'get_game', 'tournament', 'get_lan')
    search_fields = ('name', 'profiles')

    def get_game(self, team):
        return team.tournament.game

    get_game.short_description = 'spil'

    def get_lan(self, team):
        return team.tournament.lan

    get_lan.short_description = 'lan'


@admin.register(FoodOrder)
class FoodOrderAdmin(admin.ModelAdmin):
    list_filter = ('time',)
    list_display = ('pk', 'time', 'get_lan', 'order', 'get_profile', 'price', 'paid')
    search_fields = ('lanprofile__profile__user__first_name', 'lanprofile__profile__user__username', 'order', 'pk')

    def get_profile(self, food_order):
        return food_order.lanprofile.profile

    get_profile.short_description = 'profil'

    def get_lan(self, food_order):
        return food_order.lanprofile.lan

    get_lan.short_description = 'lan'

    actions = ['paid', 'not_paid']

    def paid(self, request, queryset):
        queryset.update(paid=True)

    paid.short_description = "Makér som betalt."

    def not_paid(self, request, queryset):
        queryset.update(paid=False)

    not_paid.short_description = mark_safe(mark_safe("Markér som ikke betalt."))

admin.site.register(Game)


def table_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="borde.pdf"'

    width, height = A4[1], A4[0]

    c = canvas.Canvas(response, pagesize=(width, height))
    c.setCreator('HTXAarhusLAN.dk')

    tables = get_next_lan().parse_seats()[0]

    origins = {}
    lengths = Counter(), Counter()

    for y, table in enumerate(tables):
        for x, seat in enumerate(table):
            if seat[0] is not None:
                if seat[0][0] not in origins:
                    origins[seat[0][0]] = (x, y)
                if lengths[0][seat[0][0]] < x - origins[seat[0][0]][0]:
                    lengths[0][seat[0][0]] = x - origins[seat[0][0]][0]
                if lengths[1][seat[0][0]] < y - origins[seat[0][0]][1]:
                    lengths[1][seat[0][0]] = y - origins[seat[0][0]][1]

    horizontal = {table: lengths[0][table] > lengths[1][table] for table in lengths[0]}
    pages = {seat[0]: seat[1] for table in tables for seat in table if seat[0] is not None}

    def sort(page):
        if horizontal[page[0][0]]:
            return page[0]
        else:
            n = int(page[0][1:])
            return page[0][0] + ('Z' if n % 2 == 0 else '') + str(n).zfill(2)

    pages = sorted(pages.items(), key=sort)

    def string(c, x, y, size, text):
        c.setFontSize(size)
        for i in range(len(text)):
            if c.stringWidth(text[:i]) > width * 0.8:
                text = text[:i] + '...'
                break
        c.drawCentredString(x, y, text)

    for seat, lp in pages:
        string(c, width / 2, height * 0.6, 250, seat)
        if lp is None:
            line1 = 'Denne plads er ikke reserveret.'
            line2 = 'Du kan derfor godt sætte dig her.'
        else:
            line1 = lp.profile.user.first_name
            line2 = '{}({})'.format(lp.profile.user.username, lp.profile.grade)
        string(c, width / 2, height * 0.48, 45, line1)
        string(c, width / 2, height * 0.36, 35, line2)

        c.setFontSize(12)
        c.drawString(width * 0.05, height * 0.12,
                     'Der kan være sket ændringer siden denne seddel blev printet.')
        c.drawString(width * 0.05, height * 0.1,
                     'Hvis du er i tvivl spørg et crew member eller check på htxaarhuslan.dk/tilmeld.')
        c.drawString(width * 0.05, height * 0.08,
                     'Ved ophold til lan skal du følge reglerne på htxaarhuslan.dk/info#regler.')

        c.drawImage(str(Path('main/static/main/img/logo.png')), width * 0.6, height * 0.07, width=width * 0.35,
                    preserveAspectRatio=True, anchor='sw', mask='auto')

        c.showPage()

    c.save()

    return response


def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            url(r'^pdf/bordkort.pdf/$', admin.site.admin_view(table_pdf))
        ]
        return my_urls + urls

    return get_urls


admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
