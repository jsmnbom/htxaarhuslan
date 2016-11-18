from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from main.forms import LanProfileAdminForm
from .models import Profile, Lan, LanProfile

admin.site.unregister(User)


@admin.register(LanProfile)
class LanProfileAdmin(admin.ModelAdmin):
    list_filter = ('lan__name',)
    list_display = ('profile', 'lan', 'seat')
    search_fields = ('profile__user__first_name', 'profile__user__username', 'seat')
    form = LanProfileAdminForm


class ProfileInline(admin.StackedInline):
    model = Profile


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

admin.site.register(Lan)
