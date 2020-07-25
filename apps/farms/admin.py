from django.contrib import admin
from django.db import models
from django.db.models import Sum, F
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.farms.models import Farm, CropType, Field, Crop, FarmAsset, Expense, Output


from farm_management_system.admin import ReadOnlyModelAdmin


class FarmAdmin(ReadOnlyModelAdmin):
    list_display = ('name', 'owner')

    class Meta:
        model = Farm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(owner=request.user)
        return queryset

    def has_module_permission(self, request):
        return True if request.user.is_superuser else False


class CropTypeAdmin(ReadOnlyModelAdmin):
    list_display = ['id', 'name', 'description']

    class Meta:
        model = CropType


class FieldAdmin(ReadOnlyModelAdmin):
    list_display = ('farm', 'name', 'location', 'is_own_property', 'has_electricity_tubewell', 'has_canal_irrigation',
                    'total_acres', 'landlord_name', 'landlord_number', 'lease_per_acre', 'lease_start', 'lease_end',
                    'is_active')

    class Meta:
        model = Field

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(farm__owner=request.user)
        return queryset


class CropAdmin(ReadOnlyModelAdmin):
    list_display = ['field', 'crop_type', 'season', 'breed', 'total_acres', 'total_expenses', '_total_output',
                    '_net_profit', 'date_sowing', 'date_harvesting']

    class Meta:
        model = Crop

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(field__farm__owner=request.user)
        queryset = queryset.annotate(
            total_output=Sum(
                F('crop_outputs__total_mann')*F('crop_outputs__rate_per_mann'),
                output_field=models.FloatField()
            ))
        return queryset

    def _total_output(self, obj):
        return obj.total_output
    _total_output.short_description = _('Total Output')

    def _net_profit(self, obj):
        profit = obj.total_output - obj.total_expenses
        color = 'red' if profit < 0 else 'green'
        profit = "{:.2f}".format(profit)
        profit = mark_safe(f'<span style="color: {color};">{profit}</span>')
        print(profit)
        return profit

    _net_profit.short_description = _('Net Profit')


class FarmAssetAdmin(ReadOnlyModelAdmin):
    list_display = ['farm', 'name', 'date_purchased', 'is_bought_new', 'purchase_cost']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(farm__owner=request.user)
        return queryset

    class Meta:
        model = FarmAsset


class ExpenseAdmin(ReadOnlyModelAdmin):
    list_display = ['crop', 'expense_type', 'expense_date', 'amount', 'notes', 'expend_by', 'added_by']

    class Meta:
        model = Expense

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(crop__field__farm__owner=request.user)
        return queryset


class OutputAdmin(ReadOnlyModelAdmin):
    list_display = ['crop', 'total_mann', 'rate_per_mann', 'sold_date', 'notes', '_total_output']

    class Meta:
        model = Output

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(crop__field__farm__owner=request.user)
        return queryset

    def _total_output(self, obj):
        return obj.total_mann * obj.rate_per_mann

    _total_output.short_description = _("Total Output")


admin.site.register(Farm, FarmAdmin)
admin.site.register(CropType, CropTypeAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Crop, CropAdmin)
admin.site.register(FarmAsset, FarmAssetAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Output, OutputAdmin)
