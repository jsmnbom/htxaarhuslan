from django.contrib.admin import SimpleListFilter

from main.models import Lan, get_next_lan


class LanFilter(SimpleListFilter):
    title = 'lan'
    parameter_name = 'lan'

    def lookups(self, request, model_admin):
        return [(str(lan.pk), str(lan)) for lan in Lan.objects.all().order_by('-end')] + [('all', 'Vis alle')]

    def queryset(self, request, queryset):
        value = self.value()
        if value and value != 'all':
            return queryset.filter(lan_id=value)
        return queryset

    def value(self):
        # What would the value have been?
        value = super().value()
        if value is None:
            lan = get_next_lan()
            if lan:
                value = lan.pk
            else:
                return None
        return str(value)
