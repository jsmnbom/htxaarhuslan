from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from sorl.thumbnail.admin import AdminImageMixin

from main.admin.filters import LanFilter
from main.admin.forms import AdminLanProfileForm, AdminProfileForm
from main.models import LanProfile, Profile

# Very important to do first
admin.site.unregister(User)


@admin.register(LanProfile)
class LanProfileAdmin(admin.ModelAdmin):
    list_filter = (LanFilter, 'paytype', 'paid', 'profile__grade', 'profile__user__groups')
    list_display = ('pk', 'profile', 'lan', 'seat', 'get_paytype', 'paid')
    list_display_links = ('pk', 'profile')
    search_fields = ('profile__user__first_name', 'profile__user__username', 'seat')
    form = AdminLanProfileForm

    def get_paytype(self, obj):
        return obj.get_paytype_display()

    get_paytype.short_description = LanProfile._meta.get_field('paytype').verbose_name

    actions = ['paid', 'not_paid']

    def paid(self, request, queryset):
        queryset.update(paid=True)

    paid.short_description = "Makér som betalt."

    def not_paid(self, request, queryset):
        queryset.update(paid=False)

    not_paid.short_description = mark_safe(mark_safe("Markér som ikke betalt."))


class ProfileInline(AdminImageMixin, admin.StackedInline):
    model = Profile
    form = AdminProfileForm


@admin.register(User)
class MyUserAdmin(UserAdmin):
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return self.readonly_fields + ('is_staff', 'is_superuser',
                                       'groups', 'user_permissions')

    list_display = ('username', 'email', 'first_name', 'get_grade', 'is_staff')

    def get_grade(self, user):
        return user.profile.grade

    get_grade.short_description = 'Klasse'

    inlines = [
        ProfileInline
    ]

    list_filter = UserAdmin.list_filter + ('profile__grade',)