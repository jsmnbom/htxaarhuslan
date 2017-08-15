from django.contrib.admin import SimpleListFilter
from django.core.exceptions import FieldError

from main.models import Lan, get_next_lan


class LanFilter(SimpleListFilter):
    title = 'lan'
    parameter_name = 'lan'

    lan = None

    def lookups(self, request, model_admin):
        return [(str(lan.pk), str(lan)) for lan in Lan.objects.all().order_by('-end')] + [('all', 'Vis alle')]

    def queryset(self, request, queryset):
        value = self.value()
        if value and value != 'all':
            try:
                return queryset.filter(lan_id=value)
            except FieldError:
                return queryset.filter(tournament__lan_id=value)
        return queryset

    def value(self):
        # What would the value have been?
        value = super().value()
        if value is None:
            if self.lan is None:
                self.lan = get_next_lan()
            if self.lan:
                value = self.lan.pk
            else:
                return None
        return str(value)
