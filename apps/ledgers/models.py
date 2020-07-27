from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from apps.farms.models import TimeStampedModel, Farm


class Ledger(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.PROTECT, verbose_name=_('Farm'), related_name='ledgers')
    name = models.CharField(max_length=500, verbose_name=_("Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    contact_number = models.CharField(max_length=220, blank=True, null=True, verbose_name=_("Contact number"))
    location = models.CharField(max_length=550, null=True, blank=True, verbose_name=_("Location"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Ledger')
        verbose_name_plural = _('Ledgers')


class LedgerEntries(TimeStampedModel):
    DEBIT = 1
    CREDIT = 2

    TYPE_CHOICES = (
        (DEBIT, _('Debit')),
        (CREDIT, _('Credit'))
    )

    ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT, verbose_name=_('Ledger'), related_name='entries')
    type = models.IntegerField(verbose_name=_('Type'), choices=TYPE_CHOICES)
    amount = models.FloatField(verbose_name=_('Amount'), validators=[MinValueValidator(1.0)])
    transaction_date = models.DateTimeField(blank=True, verbose_name=_("Transaction date"), default=now)
    notes = models.TextField(blank=True, null=True, verbose_name=_('Notes'))

    def __str__(self):
        return f"{self.ledger}({self.type}) {self.amount}"

    class Meta:
        verbose_name = _('Ledger Entry')
        verbose_name_plural = _('Ledger Entries')
