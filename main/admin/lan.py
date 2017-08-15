from django.contrib import admin
from django.forms import model_to_dict
from django.urls import reverse
from django.utils.timezone import now

from main.models import Lan, Event


class EventInline(admin.TabularInline):
    model = Event
    show_change_link = True

    fields = ('name', 'url', 'start', 'end')


@admin.register(Lan)
class LanAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'seats_count', 'is_open', 'bordkort')

    fieldsets = (
        ('Tider', {
            'fields': (('start', 'end'), 'open', 'show_calendar')
        }),
        ('Pladser', {
            'fields': ('seats',)
        }),
        ('Tekst', {
            'fields': ('name', 'blurb')
        }),
        ('Betaling', {
            'fields': ('paytypes', 'price', 'payphone', 'payment_manager_id')
        }),
        ('Madbestilling', {
            'fields': ('food_open', 'food_phone')
        }),
    )

    inlines = [
        EventInline
    ]

    def get_changeform_initial_data(self, request):
        try:
            prev_lan = Lan.objects.filter(start__lt=now()).order_by("-start")[0]
            return model_to_dict(prev_lan, ['blurb', 'seats', 'schedule'])
        except (Lan.DoesNotExist, AttributeError, IndexError):
            return {}

    def bordkort(self, lan):
        return '<a href="{}">Download bordkort</a>'.format(reverse('admin:bordkort', kwargs={'lan_id': lan.id}))

    bordkort.allow_tags = True
    bordkort.short_description = 'Bordkort'
