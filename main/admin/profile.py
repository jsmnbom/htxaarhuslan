from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from sorl.thumbnail import ImageField
from sorl.thumbnail.admin.current import AdminImageWidget

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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile').select_related('profile__user')

    def get_paytype(self, obj):
        return obj.get_paytype_display()

    get_paytype.short_description = LanProfile._meta.get_field('paytype').verbose_name
    get_paytype.admin_sort_field = 'paytype'

    actions = ['paid', 'not_paid']

    def paid(self, request, queryset):
        queryset.update(paid=True)

    paid.short_description = "Makér som betalt."

    def not_paid(self, request, queryset):
        queryset.update(paid=False)

    not_paid.short_description = "Markér som ikke betalt."


# We need to patch renderer= in AdminImageWidget since it's not django 2.1 ready yet

class ProfileAdminImageWidget(AdminImageWidget):
    def render(self, name, value, attrs=None, renderer=None):
        return super().render(name, value, attrs=attrs)


class ProfileAdminImageMixin(object):
    """
    This is a mix-in for InlineModelAdmin subclasses to make ``ImageField``
    show nicer form widget
    """

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            return db_field.formfield(widget=ProfileAdminImageWidget)
        sup = super(ProfileAdminImageMixin, self)
        return sup.formfield_for_dbfield(db_field, **kwargs)


class ProfileInline(ProfileAdminImageMixin, admin.StackedInline):
    model = Profile
    form = AdminProfileForm


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'get_grade', 'is_staff')

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return self.readonly_fields + ('is_staff', 'is_superuser',
                                       'groups', 'user_permissions')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')

    def get_grade(self, user):
        return user.profile.grade

    get_grade.short_description = 'Klasse'
    get_grade.admin_order_field = 'profile__grade'

    inlines = [
        ProfileInline
    ]

    list_filter = UserAdmin.list_filter + ('profile__grade',)
