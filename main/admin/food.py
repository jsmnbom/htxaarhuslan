from django.contrib import admin
from django.utils.safestring import mark_safe

from main.models import FoodOrder


@admin.register(FoodOrder)
class FoodOrderAdmin(admin.ModelAdmin):
    list_filter = ('time',)
    list_display = ('pk', 'time', 'get_lan', 'order', 'get_profile', 'price', 'paid')
    search_fields = ('lanprofile__profile__user__first_name', 'lanprofile__profile__user__username', 'order')

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
