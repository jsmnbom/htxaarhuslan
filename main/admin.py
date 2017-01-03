from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import ProgrammingError
from django.forms import model_to_dict
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from sorl.thumbnail.admin import AdminImageMixin

from main.forms import AdminLanProfileForm, AdminProfileForm
from .models import Profile, Lan, LanProfile, get_next_lan, Tournament, Game, TournamentTeam

admin.site.unregister(User)


class DefaultFilterMixIn(admin.ModelAdmin):
    def changelist_view(self, request, *args, **kwargs):
        from django.http import HttpResponseRedirect
        if self.default_filters:
            try:
                test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
                if test and test[-1] and not test[-1].startswith('?'):
                    url = reverse('admin:%s_%s_changelist' % (self.opts.app_label, self.opts.model_name))
                    filters = []
                    for filt in self.default_filters:
                        key = filt.split('=')[0]
                        if key not in request.GET:
                            filters.append(filt)
                    if filters:
                        return HttpResponseRedirect("%s?%s" % (url, "&".join(filters)))
            except KeyError:
                pass
        return super(DefaultFilterMixIn, self).changelist_view(request, *args, **kwargs)


@admin.register(LanProfile)
class LanProfileAdmin(DefaultFilterMixIn, admin.ModelAdmin):
    list_filter = ('lan', 'paytype', 'paid')
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

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        try:
            if get_next_lan():
                self.default_filters = ('lan__id__exact={}'.format(get_next_lan().id),)
        except ProgrammingError:
            pass


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
            'fields': (('start', 'end'), 'open')
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
    list_filter = ('lan', 'game')
    list_display = ('name', 'game', 'lan', 'challonge_link', 'get_teams_count', 'live', 'open')
    search_fields = ('name', 'game', 'lan')

    inlines = [
        TournamentTeamInline
    ]

    def get_teams_count(self, tournament):
        return tournament.tournamentteam_set.count()

    get_teams_count.short_description = 'Antal hold'

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        try:
            if get_next_lan():
                self.default_filters = ('lan__id__exact={}'.format(get_next_lan().id),)
        except ProgrammingError:
            pass

    def challonge_link(self, tournament):
        return '<a href="http://challonge.com/{0}" target="_blank">{0}</a>'.format(tournament.get_challonge_url())

    challonge_link.allow_tags = True
    challonge_link.short_description = 'Challonge'


admin.site.register(Game)
admin.site.register(TournamentTeam)
