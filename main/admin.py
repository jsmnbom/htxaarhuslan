from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from sorl.thumbnail.admin import AdminImageMixin

from main.forms import AdminLanProfileForm, AdminProfileForm
from .models import Profile, Lan, LanProfile, Tournament, Game, TournamentTeam, Event, get_next_lan

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
    )

    def get_changeform_initial_data(self, request):
        try:
            prev_lan = Lan.objects.filter(start__lt=now()).order_by("-start")[0]
            return model_to_dict(prev_lan, ['blurb', 'seats', 'schedule'])
        except (Lan.DoesNotExist, AttributeError, IndexError):
            return {}


class TournamentTeamInline(admin.TabularInline):
    model = TournamentTeam
    fields = ('profiles', 'name')


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


admin.site.register(Game)
admin.site.register(TournamentTeam)
admin.site.register(Event)
