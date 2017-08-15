from django.contrib import admin

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

    actions = ['paid', 'not_paid']

    def paid(self, request, queryset):
        queryset.update(paid=True)

    paid.short_description = "Makér som betalt."

    def not_paid(self, request, queryset):
        queryset.update(paid=False)

    not_paid.short_description = "Markér som ikke betalt."
