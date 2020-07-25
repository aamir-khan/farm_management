from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


from farm_management_system.admin import ReadOnlyModelAdmin


class EmployeeAdmin(ReadOnlyModelAdmin, UserAdmin):

    list_display = ('id', '_name')

    def get_queryset(self, request):
        queryset = super(EmployeeAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(pk=request.user.pk)
        # queryset2 = queryset.annotate(total_expenses=Sum('user__ledgers__amount'))
        return queryset

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    class Meta:
        model = User

    @staticmethod
    def _name(obj):
        return obj.get_full_name() or obj.username
    _name.short_description = "Name"

    def get_list_filter(self, request):
        if not request.user.is_superuser:
            return []
        return self.list_filter

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly_fields.extend(
                ['is_superuser', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
                 ])
            readonly_fields = tuple(readonly_fields)
        return readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()  # type: Set[str]

        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
                'date_joined',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form


admin.site.unregister(Group)

admin.site.register(User, EmployeeAdmin)
