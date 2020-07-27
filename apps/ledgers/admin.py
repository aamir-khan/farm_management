from django.contrib import admin
from django.db.models import OuterRef, Sum, Subquery, IntegerField, F
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.ledgers.models import Ledger, LedgerEntries


from farm_management_system.admin import ReadOnlyModelAdmin


class BalanceFilter(admin.SimpleListFilter):
    title = _('By Balance')
    parameter_name = 'balance'

    def lookups(self, request, model_admin):
        return (
            ('debt', _('More Debt')),
            ('credit', _('More credit')),
            ('balanced', _('Balanced'))
        )

    def queryset(self, request, queryset):
        """Return the filtered queryset"""

        if self.value() == 'debt':
            return queryset.filter(total_debt__gt=F('total_credit'))
        elif self.value() == 'credit':
            return queryset.filter(total_debt__lt=F('total_credit'))
        elif self.value() == 'balanced':
            return queryset.filter(total_debt=F('total_credit'))
        else:
            return queryset
#
#
# class FarmAdmin(ReadOnlyModelAdmin):
#     list_display = ('name', 'owner')
#
#     class Meta:
#         model = Farm
#
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         if not request.user.is_superuser:
#             queryset = queryset.filter(owner=request.user)
#         return queryset
#
#     def has_module_permission(self, request):
#         return True if request.user.is_superuser else False
#
#
# class CropTypeAdmin(ReadOnlyModelAdmin):
#     list_display = ['id', 'name', 'description']
#
#     class Meta:
#         model = CropType
#
#
# class FieldAdmin(ReadOnlyModelAdmin):
#     list_display = ('farm', 'name', 'location', 'is_own_property', 'has_electricity_tubewell', 'has_canal_irrigation',
#                     'total_acres', 'landlord_name', 'landlord_number', 'lease_per_acre', 'lease_start', 'lease_end',
#                     'is_active')
#
#     class Meta:
#         model = Field
#
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         if not request.user.is_superuser:
#             queryset = queryset.filter(farm__owner=request.user)
#         return queryset
#
#


class LedgersEntriesInline(admin.TabularInline):
    model = LedgerEntries
    extra = 0

    class Meta:
        pass


class LedgerAdmin(ReadOnlyModelAdmin):
    list_display = ['id', 'name', 'description', 'location', 'is_active', '_total_debt', '_total_credit',
                    '_net_balance']

    list_filter = ['name', BalanceFilter]

    inlines = [LedgersEntriesInline]

    class Meta:
        model = Ledger

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(farm__owner=request.user)

        total_debt = Ledger.objects.filter(pk=OuterRef('pk'), entries__type=LedgerEntries.DEBIT).annotate(
            total_debt=Sum(
                'entries__amount'
            ))
        total_credit = Ledger.objects.filter(pk=OuterRef('pk'), entries__type=LedgerEntries.CREDIT).annotate(
            total_credit=Sum(
                'entries__amount'
            ))

        queryset = queryset.annotate(
            total_debt=Coalesce(Subquery(total_debt.values('total_debt'), output_field=IntegerField()), 0),
            total_credit=Coalesce(Subquery(total_credit.values('total_credit'), output_field=IntegerField()), 0)
        )
        return queryset

    def _total_debt(self, obj):
        url = reverse(f'admin:ledgers_ledgerentries_changelist')
        url += f'?ledger__id__exact={obj.id}&type__exact={LedgerEntries.DEBIT}'
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.total_debt)
    _total_debt.short_description = _('Total Debt')

    def _total_credit(self, obj):
        url = reverse(f'admin:ledgers_ledgerentries_changelist')
        url += f'?ledger__id__exact={obj.id}&type__exact={LedgerEntries.CREDIT}'
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.total_credit)

    _total_credit.short_description = _("Total Credit")

    def _net_balance(self, obj):
        balance = obj.total_credit - obj.total_debt
        color = 'red' if balance < 0 else 'green'
        balance = "{:.2f}".format(balance)
        return mark_safe(f'<span style="color: {color};">{balance}</span>')

    _net_balance.short_description = _('Net Balance')


class LedgerEntriesAdmin(ReadOnlyModelAdmin):
    list_display = ['id', 'ledger', 'type', 'amount', 'transaction_date', 'notes']

    list_filter = ('ledger', 'type')

    class Meta:
        model = LedgerEntries

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(ledger__farm__owner=request.user)
        return queryset


admin.site.register(Ledger, LedgerAdmin)
admin.site.register(LedgerEntries, LedgerEntriesAdmin)
