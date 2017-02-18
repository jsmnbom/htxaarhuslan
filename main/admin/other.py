from django.contrib import admin

from main.admin.filters import LanFilter
from main.models import Game, Event

admin.site.register(Game)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_filter = (LanFilter,)
    list_display = ('name', 'lan', 'start', 'end')
    search_fields = ('name', 'description')
