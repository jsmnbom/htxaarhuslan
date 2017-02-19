from django.contrib import admin
from rest_framework.authtoken.models import Token

from main.admin.filters import LanFilter
from main.models import Game, Event

admin.site.register(Game)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_filter = (LanFilter,)
    list_display = ('name', 'lan', 'start', 'end')
    search_fields = ('name', 'description')


admin.site.unregister(Token)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created')
    fields = ('user',)
    ordering = ('-created',)
