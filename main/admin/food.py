from collections import Counter, OrderedDict

from django.contrib import admin
from django.http import HttpResponse

from main.models import FoodOrder


@admin.register(FoodOrder)
class FoodOrderAdmin(admin.ModelAdmin):
    list_filter = ('time',)
    list_display = ('pk', 'time', 'get_lan', 'order', 'get_profile', 'price', 'paid')
    list_display_links = ('pk', 'time', 'order')
    search_fields = ('lanprofile__profile__user__first_name', 'lanprofile__profile__user__username', 'order')

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .select_related('lanprofile')
                .select_related('lanprofile__profile')
                .select_related('lanprofile__profile__user'))

    def get_profile(self, food_order):
        return food_order.lanprofile.profile

    get_profile.short_description = 'profil'
    get_profile.admin_order_field = 'lanprofile__profile'

    def get_lan(self, food_order):
        return food_order.lanprofile.lan

    get_lan.short_description = 'lan'
    get_lan.admin_order_field = 'lanprofile__lan'

    actions = ['paid', 'not_paid', 'generate_summary']

    def paid(self, request, queryset):
        queryset.update(paid=True)

    paid.short_description = "Makér som betalt."

    def not_paid(self, request, queryset):
        queryset.update(paid=False)

    not_paid.short_description = "Markér som ikke betalt."

    def generate_summary(self, request, queryset):
        out = Counter()
        for order in queryset:
            out[str(order)] += 1
        out = OrderedDict(sorted(out.items(), key=lambda x: x[0]))
        texts, last = [], ''
        for key, value in out.items():
            splitted = [x.strip() for x in key.split('-')]

            if splitted[0] != last:
                texts.append('')
                last = splitted[0]

            key = ' - '.join(splitted[1:])
            texts.append('{} stk. {}'.format(value, key))

        texts = texts[1:]
        response = HttpResponse('\r\n'.join(texts), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="Madbestillinger.txt"'
        return response

    generate_summary.short_description = "Vis oversigt."
