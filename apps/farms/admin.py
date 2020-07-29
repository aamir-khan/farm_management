from django.contrib import admin
from django.db import models
from django.db.models import F, IntegerField, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.farms.models import Farm, CropType, Field, Crop, FarmAsset, Expense, Output
from apps.users.models import User

from farm_management_system.admin import ReadOnlyModelAdmin
from django.contrib.admin.filters import RelatedFieldListFilter


class ProfitFilter(admin.SimpleListFilter):
    title = _('By Profit')
    parameter_name = 'profit'

    def lookups(self, request, model_admin):
        return (
            ('profitable', _('Profitable')),
            ('loss', _('Loss')),
            ('balanced', _('Balanced')),
        )

    def queryset(self, request, queryset):
        """Return the filtered queryset"""

        if self.value() == 'profitable':
            return queryset.filter(total_output__gt=F('total_expense'))
        elif self.value() == 'loss':
            return queryset.filter(total_output__lt=F('total_expense'))
        elif self.value() == 'balanced':
            return queryset.filter(total_output=F('total_expense'))
        else:
            return queryset


class FieldFilter(RelatedFieldListFilter):

    def field_choices(self, field, request, model_admin):
        farm_fields = Field.objects.all()
        if not request.user.is_superuser:
            farm_fields = farm_fields.filter(farm__owner=request.user)
        return field.get_choices(include_blank=False, limit_choices_to={'pk__in': farm_fields})


class CropFilter(RelatedFieldListFilter):

    def field_choices(self, field, request, model_admin):
        crops = Crop.objects.all()
        if not request.user.is_superuser:
            crops = crops.filter(field__farm__owner=request.user)
        return field.get_choices(include_blank=False, limit_choices_to={'pk__in': crops})


class ExpenseInlineAdmin(admin.TabularInline):
    model = Expense
    extra = 0


class FarmAdmin(ReadOnlyModelAdmin):
    list_display = ('name', 'owner')

    class Meta:
        model = Farm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(owner=request.user)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'owner' and not request.user.is_superuser:
            kwargs['queryset'] = User.objects.filter(pk=request.user.pk)
            kwargs['initial'] = request.user.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'farm' and not request.user.is_superuser:
            kwargs['queryset'] = Farm.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CropAdmin(ReadOnlyModelAdmin):
    list_display = ['field', '_crop', 'total_expenses', '_total_output', '_net_profit', '_expense_per_acre',
                    '_output_per_acre', '_net_profit_per_acre', 'breed', 'total_acres',  'date_sowing',
                    'date_harvesting']

    list_filter = [('field', FieldFilter), 'crop_type', 'season', 'date_sowing', ProfitFilter]

    ordering = ('-date_sowing', )

    inlines = [ExpenseInlineAdmin]

    class Meta:
        model = Crop

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            if 'field__farm__owner' not in list_filter:
                list_filter.append('field__farm__owner')
        else:
            if 'field__farm__owner' in list_filter:
                list_filter.remove('field__farm__owner')
        return list_filter

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(field__farm__owner=request.user)

        total_output = Crop.objects.filter(pk=OuterRef('pk')).annotate(
            total_output=Sum(
                F('crop_outputs__total_mann') * F('crop_outputs__rate_per_mann'),
                output_field=models.FloatField()
            ))
        total_expense = Crop.objects.filter(pk=OuterRef('pk')).annotate(total_expense=Sum('crop_expenses__amount'))

        queryset = queryset.annotate(
            total_output=Coalesce(Subquery(total_output.values('total_output'), output_field=IntegerField()), 0),
            total_expense=Coalesce(Subquery(total_expense.values('total_expense'), output_field=IntegerField()), 0)
        )
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'field' and not request.user.is_superuser:
            kwargs['queryset'] = Field.objects.filter(farm__owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def _total_output(self, obj):
        url = reverse(f'admin:farms_output_changelist')
        url += f'?crop__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj.total_output)
    _total_output.short_description = _('Total Output')

    def total_expenses(self, obj):
        url = reverse(f'admin:farms_expense_changelist')
        url += f'?crop__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj.total_expense)

    total_expenses.short_description = _("Total Expenses")

    def _net_profit(self, obj):
        profit = obj.total_output - obj.total_expense
        color = 'red' if profit < 0 else 'green'
        profit = "{:.2f}".format(profit)
        profit = mark_safe(f'<span style="color: {color};">{profit}</span>')
        return profit

    _net_profit.short_description = _('Net Profit')

    def _expense_per_acre(self, obj):
        per_acre_expenses = obj.total_expense / obj.total_acres
        per_acre_expenses = "{:.2f}".format(per_acre_expenses)
        return per_acre_expenses

    _expense_per_acre.short_description = _("Expenses per acre")

    def _output_per_acre(self, obj):
        per_acre_output = obj.total_output / obj.total_acres
        per_acre_output = "{:.2f}".format(per_acre_output)
        return per_acre_output

    _output_per_acre.short_description = _("Output per acre")

    def _net_profit_per_acre(self, obj):
        profit = (obj.total_output - obj.total_expense) / obj.total_acres
        color = 'red' if profit < 0 else 'green'
        profit = "{:.2f}".format(profit)
        profit = mark_safe(f'<span style="color: {color};">{profit}</span>')
        return profit

    _net_profit_per_acre.short_description = _('Profit per acre')

    def _crop(self, obj):
        return f"{obj.crop_type}({obj.get_season_display()})"

    _crop.short_description = _("Crop")


class FarmAssetAdmin(ReadOnlyModelAdmin):
    list_display = ['farm', 'name', 'date_purchased', 'is_bought_new', 'purchase_cost']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(farm__owner=request.user)
        return queryset

    class Meta:
        model = FarmAsset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'farm' and not request.user.is_superuser:
            kwargs['queryset'] = Farm.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ExpenseAdmin(ReadOnlyModelAdmin):
    list_display = ['crop', '_expense_type', 'amount', 'expense_date', 'notes', 'spent_by', 'added_by']

    list_filter = [('crop', CropFilter), 'spent_by', 'expense_type']

    class Meta:
        model = Expense

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(crop__field__farm__owner=request.user)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'crop' and not request.user.is_superuser:
            kwargs['queryset'] = Crop.objects.filter(field__farm__owner=request.user)
        elif db_field.name == 'spent_by' and not request.user.is_superuser:
            kwargs['queryset'] = User.objects.filter(pk=request.user.pk)
        elif db_field.name == 'added_by' and not request.user.is_superuser:
            kwargs['queryset'] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def _expense_type(self, obj):
        return obj.get_expense_type_display()

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            if 'crop__field__farm' not in list_filter:
                list_filter.append('crop__field__farm')
        else:
            if 'crop__field__farm' in list_filter:
                list_filter.remove('crop__field__farm')
        return list_filter

    _expense_type.short_description = _("Type")


class OutputAdmin(ReadOnlyModelAdmin):
    list_display = ['crop', 'total_mann', 'rate_per_mann', 'sold_date', 'notes', '_total_output']

    list_filter = [('crop', CropFilter), ('crop__field', FieldFilter)]

    class Meta:
        model = Output

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(crop__field__farm__owner=request.user)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'crop' and not request.user.is_superuser:
            kwargs['queryset'] = Crop.objects.filter(field__farm__owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            if 'crop__field__farm' not in list_filter:
                list_filter.append('crop__field__farm')
        else:
            if 'crop__field__farm' in list_filter:
                list_filter.remove('crop__field__farm')
        return list_filter

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
