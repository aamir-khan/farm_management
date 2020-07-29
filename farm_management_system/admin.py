from django.contrib import admin

from django.contrib.admin.options import flatten_fieldsets
from django.contrib.admin.templatetags.admin_modify import register
from django.contrib.admin.templatetags.admin_modify import submit_row as original_submit_row


class ReadOnlyModelAdmin(admin.ModelAdmin):
    pass
    # """
    # ModelAdmin class that prevents modifications through the admin.
    # The changelist and the detail view work, but a 403 is returned
    # if one actually tries to edit an object.
    # Source: https://gist.github.com/aaugustin/1388243
    # """
    # actions = None
    #
    # # We cannot call super().get_fields(request, obj) because that method calls
    # # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # # super().get_form(request, obj). So we  assume the default ModelForm.
    # def get_readonly_fields(self, request, obj=None):
    #     if request.user.is_superuser:
    #         return []
    #     return self.fields or [f.name for f in self.model._meta.fields]
    #
    # def has_change_permission(self, request, obj=None):
    #     return True if request.user.is_superuser else (request.method in ['GET', 'HEAD'] and
    #                                                    request.user.is_staff)
    #
    # def has_module_permission(self, request):
    #     return request.user.is_superuser or request.user.is_staff
    #
    # def get_readonly_fields(self, request, obj=None):
    #     user = request.user
    #     if user.is_staff and not user.is_superuser:
    #         if self.fieldsets:
    #             return flatten_fieldsets(self.fieldsets or [])
    #         else:
    #             return list(set(
    #                 [field.name for field in self.opts.local_fields] +
    #                 [field.name for field in self.opts.local_many_to_many]))
    #
    #     return super().get_readonly_fields(request, obj)
    #
    # @register.inclusion_tag('admin/submit_line.html', takes_context=True)
    # def submit_row(context):
    #     ctx = original_submit_row(context)
    #
    #     user = context['request'].user
    #     if user.is_staff and not user.is_superuser:
    #         ctx.update({
    #             'show_save_and_add_another': False,
    #             'show_save_and_continue': False,
    #             'show_save': False,
    #             'show_save_as_new': False,
    #         })
    #     return ctx
    #
    # def has_view_permission(self, request, obj=None):
    #     return request.user.is_staff
