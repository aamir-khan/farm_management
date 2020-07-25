from enum import Enum

from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext as _

from apps.users.models import User


class TimeStampedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Farm(TimeStampedModel):
    name = models.CharField(max_length=550, verbose_name=_('Farm Name'), null=False, blank=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        permissions = (
            ('can_view_farm', 'Can View Farm'),
        )

    def __str__(self):
        return f"{self.name}({self.owner})"


class FarmAsset(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.PROTECT)
    name = models.CharField(max_length=550, verbose_name=_('Asset Name'), null=False, blank=False)
    date_purchased = models.DateTimeField()
    is_bought_new = models.BooleanField()
    purchase_cost = models.IntegerField(help_text='Amount in thousands rupees')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        permissions = (
            ('can_view_farmAsset', 'Can View FarmAsset'),
        )


class EnumBase(Enum):
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Crop(TimeStampedModel):
    name = models.CharField(max_length=550, verbose_name=_('Crop Name'), null=False, blank=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        permissions = (
            ('can_view_crop', 'Can View Crop'),
        )


class ExpenseType(EnumBase):
    SEED = 'seed'
    FERTILIZER = 'fertilizer'
    PESTICIDES = 'pesticides'
    WATER = 'water'
    ELECTRICITY_BILL = 'electricity_bill'
    OIL = 'oil'
    LABOUR = 'labour'
    MISC = 'miscellaneous'

    class Meta:
        permissions = (
            ('can_view_expenseType', 'Can View ExpenseTypes'),
        )


class Season(EnumBase):
    SUMMER = 'summer'
    WINTER = 'winter'
    MID_SEASON = 'mid_season'


class KhoohORField(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.PROTECT)
    name_urdu = models.CharField(max_length=550, verbose_name='کھوہ کا نام', null=False, blank=False)
    location = models.CharField(max_length=550, blank=True)
    is_own_property = models.BooleanField()
    has_electricity_tubewell = models.BooleanField()
    has_canal_irrigation = models.BooleanField()
    total_acres = models.FloatField()

    # If not the owner if the field
    zameendaar_name = models.CharField(help_text='Zameendaar name if not owned', blank=True, max_length=550)
    zameendaar_number = models.CharField(help_text='Zameendaar number if not owned', blank=True, max_length=550)
    per_acre_theka = models.FloatField('If leased then theka in thousands', blank=True)
    lease_start = models.DateField(blank=True)
    lease_end = models.DateField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ('can_view_khoohORField', 'Can View KhoohORField'),
        )
    
    def __str__(self):
        return f"{self.name_urdu}"


class Fasal(TimeStampedModel):
    khooh = models.ForeignKey(KhoohORField, on_delete=models.PROTECT)
    crop = models.ForeignKey(Crop, on_delete=models.PROTECT)
    season = models.CharField(choices=Season.choices(), max_length=550)
    total_acres = models.FloatField()
    date_sowing = models.DateField()
    date_harvesting = models.DateField(blank=True)

    def __str__(self):
        return f"{self.khooh}->{self.crop}"


class Expense(TimeStampedModel):
    SEED = 1
    FERTILIZER = 2
    PESTICIDES = 3
    WATER = 4
    ELECTRICITY_BILL = 5
    OIL = 6
    LABOUR = 7
    MISC = 8

    EXPENSE_TYPE_CHOICES = (
        (SEED, _('Seed')),
        (FERTILIZER, _('Fertilizer')),
        (PESTICIDES, _('Pesticides')),
        (WATER, _('Water')),
        (ELECTRICITY_BILL, _('Electricity_bill')),
        (OIL, _('Oil')),
        (LABOUR, _('Labour')),
        (MISC, _('Miscellaneous')),
    )
    fasal = models.ForeignKey(Fasal, on_delete=models.PROTECT)
    expense_type = models.CharField(
        choices=EXPENSE_TYPE_CHOICES,
        max_length=255
    )
    expense_date = models.DateField(null=False)
    amount = models.FloatField(null=False, blank=False)
    notes = models.TextField(null=True)

    expend_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='expenditures')
    added_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='added_expenditures')

    class Meta:
        ordering = ('-expense_date', )
        permissions = (
            ('can_view_expense', 'Can View Expense'),
        )

    def __str__(self):
        return f"Rs. {self.amount}->{self.fasal}({self.expense_type}) by {self.expend_by}"


class Output(TimeStampedModel):
    fasal = models.ForeignKey(Fasal, on_delete=models.PROTECT)
    total_mann = models.FloatField(help_text='Total mann weight')
    rate_per_mann = models.IntegerField(help_text='Per mann rate')
    sold_date = models.DateField()

    class Meta:
        ordering = ('-sold_date', )
        permissions = (
            ('can_view_output', 'Can View Output'),
        )

    def __str__(self):
        return f"Rs. {self.fasal}->{self.total_mann}"
