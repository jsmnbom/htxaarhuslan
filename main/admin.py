from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from main.forms import AdminLanProfileForm, AdminProfileForm, AdminLanForm
from .models import Profile, Lan, LanProfile

admin.site.unregister(User)


@admin.register(LanProfile)
class LanProfileAdmin(admin.ModelAdmin):
    list_filter = ('lan__name', 'paytype', 'paid')
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

    def not_paid (self, request, queryset):
        queryset.update(paid=False)
    not_paid.short_description = mark_safe(mark_safe("Markér som ikke betalt."))


class ProfileInline(admin.StackedInline):
    model = Profile
    form = AdminProfileForm


@admin.register(User)
class MyUserAdmin(UserAdmin):
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
    form = AdminLanForm

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
