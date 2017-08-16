from django.contrib import admin

from main.admin import LanFilter
from main.models import Tournament, TournamentTeam


class TournamentTeamInline(admin.TabularInline):
    model = TournamentTeam
    show_change_link = True

    fields = ('name',)  # If we show profiles too it slows down the SQL


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_filter = (LanFilter, 'game', 'owner')
    list_display = ('name', 'game', 'lan', 'start', 'challonge_link', 'get_teams_count', 'live', 'open', 'owner')
    search_fields = ('name', 'game', 'lan')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner__user')

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

    actions = ['open', 'close']

    def open(self, request, queryset):
        queryset.update(open=True)

    open.short_description = "Åben for tilmelding."

    def close(self, request, queryset):
        queryset.update(open=False)

    close.short_description = "Luk for tilmelding."


@admin.register(TournamentTeam)
class TournamentTeamAdmin(admin.ModelAdmin):
    list_filter = (LanFilter, 'tournament__game', 'tournament')
    list_display = ('name', 'get_game', 'tournament', 'get_lan')
    search_fields = ('name', 'profiles', 'namedprofiles')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tournament').select_related('tournament__game')

    def get_game(self, team):
        return team.tournament.game

    get_game.short_description = 'spil'
    get_game.admin_order_field = 'tournament__game'

    def get_lan(self, team):
        return team.tournament.lan

    get_lan.short_description = 'lan'
    get_lan.admin_order_field = 'tournament__lan'
