from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission, Group
from django.utils.translation import gettext_lazy as _

from apps.farms.models import Farm, Crop, KhoohORField, Fasal, FarmAsset, Expense, Output



# class UserDocumentAdmin(ReadOnlyModelAdmin):
#     list_display = ('user', 'document_type', 'name', 'description', 'issued_by', 'issued_date', 'expiry_date',
#                     'image_tag')
#
#     list_filter = ('user', 'document_type')
#
#     class Meta:
#         model = UserDocument
#
#     def get_queryset(self, request):
#         queryset = super(UserDocumentAdmin, self).get_queryset(request)
#         if not request.user.is_superuser:
#             queryset = queryset.filter(user=request.user)
#         return queryset
#
#     def get_list_filter(self, request):
#         if not request.user.is_superuser:
#             return []
#         return self.list_filter

# Farm, Crop, KhoohORField, Fasal, FarmAsset, Expense, Output
from farm_management_system.admin import ReadOnlyModelAdmin


class FarmAdmin(ReadOnlyModelAdmin):
    # list_display = ('id', 'name', 'location')

    class Meta:
        model = Farm

    def has_module_permission(self, request):
        return True if request.user.is_superuser else False


class CropAdmin(ReadOnlyModelAdmin):
    # list_display = ['user', 'type', 'expense_date', 'amount', 'notes', 'time_sheet_record', 'hours', 'hourly_rate',
    #                 'trade']

    # list_filter = ['type', 'expense_date']


    class Meta:
        model = Crop

    # def get_queryset(self, request):
    #     queryset = super(LedgerAdmin, self).get_queryset(request)
    #     if not request.user.is_superuser:
    #         queryset = queryset.filter(user=request.user)
    #     return queryset

    # def get_list_filter(self, request):
    #     list_filter = self.list_filter
    #     if request.user.is_superuser:
    #         self.list_filter.append('user')
    #     return list_filter


class KhoohORFieldAdmin(ReadOnlyModelAdmin):

    # list_display = ['work_month', 'time_sheet_file', 'work_site', 'notes']

    class Meta:
        model = KhoohORField


class FasalAdmin(ReadOnlyModelAdmin):
    class Meta:
        model = Fasal


class FarmAssetAdmin(ReadOnlyModelAdmin):

    # list_display = ['work_month', 'time_sheet_file', 'work_site', 'notes']

    class Meta:
        model = FarmAsset


class ExpenseAdmin(ReadOnlyModelAdmin):

    # list_display = ['work_month', 'time_sheet_file', 'work_site', 'notes']

    class Meta:
        model = Expense


class OutputAdmin(ReadOnlyModelAdmin):

    # list_display = ['work_month', 'time_sheet_file', 'work_site', 'notes']

    class Meta:
        model = Output


admin.site.register(Farm, FarmAdmin)
admin.site.register(Crop, CropAdmin)
admin.site.register(KhoohORField, KhoohORFieldAdmin)
admin.site.register(Fasal, FasalAdmin)
admin.site.register(FarmAsset, FarmAssetAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Output, OutputAdmin)
