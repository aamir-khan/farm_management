from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from apps.users.models import User


class TimeStampedModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Farm(TimeStampedModel):
    name = models.CharField(max_length=550, verbose_name=_('farm Name'), null=False, blank=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('Owner'))

    class Meta:
        permissions = (
            ('can_view_farm', 'Can View Farm'),
        )

        verbose_name = _('Farm')
        verbose_name_plural = _('Farms')

    def __str__(self):
        return f"{self.name}({self.owner})"


class FarmAsset(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.PROTECT, verbose_name=_('Farm'))
    name = models.CharField(max_length=550, verbose_name=_('Asset Name'), null=False, blank=False)
    date_purchased = models.DateField(verbose_name=_('Date purchased'))
    is_bought_new = models.BooleanField(verbose_name=_('Is purchased new'))
    purchase_cost = models.IntegerField(help_text=_('Amount in rupees'), verbose_name=_('Purchase cost'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        permissions = (
            ('can_view_farmAsset', 'Can View FarmAsset'),
        )

        verbose_name = _('Farm Asset')
        verbose_name_plural = _('Farm Assets')


class CropType(TimeStampedModel):
    name = models.CharField(max_length=550, verbose_name=_('Crop Name'), null=False, blank=False)
    description = models.CharField(max_length=550, null=True, blank=True, verbose_name=_('Description'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        permissions = (
            ('can_view_crop', 'Can View Crop'),
        )

        verbose_name = _('Crop type')
        verbose_name_plural = _('Crop types')


class Field(TimeStampedModel):
    farm = models.ForeignKey(Farm, on_delete=models.PROTECT, verbose_name=_('Farm'))
    name = models.CharField(max_length=550, verbose_name=_('Field Name'), null=False, blank=False)
    location = models.CharField(max_length=550, blank=True, verbose_name=_('Location'))
    is_own_property = models.BooleanField(verbose_name=_('Is Own Property'))
    has_electricity_tubewell = models.BooleanField(verbose_name=_('Has Electricity tubewell'))
    has_canal_irrigation = models.BooleanField(verbose_name=_('Has Canal Irrigation'))
    total_acres = models.FloatField(verbose_name=_('Total Acres'))

    # If not the owner if the field
    landlord_name = models.CharField(
        verbose_name=_('Landlord Name'), help_text=_('Landlord name if not owned'), blank=True, max_length=550)
    landlord_number = models.CharField(
        verbose_name=_('Landlord Number'), help_text=_('Landlord number if not owned'), blank=True, max_length=550)
    lease_per_acre = models.FloatField(
        verbose_name=_('Lease per acre'), help_text=_('If leased then theka in thousands'), blank=True, null=True)
    lease_start = models.DateField(
        blank=True, verbose_name=_('Lease start'), help_text=_('Lease start date if not owned'), null=True)
    lease_end = models.DateField(
        blank=True, verbose_name=_('Lease end'), help_text=_('Lease end date if not owned'), null=True
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'), help_text=_('Is lease active'))

    class Meta:
        permissions = (
            ('can_view_field', 'Can View Field'),
        )

        verbose_name = _('Field')
        verbose_name_plural = _('Fields')
    
    def __str__(self):
        return f"{self.name}"


class Crop(TimeStampedModel):
    SUMMER = "1"
    WINTER = "2"
    MID_SEASON = "3"

    SEASON_CHOICES = (
        (SUMMER, _('Summer')),
        (WINTER, _('Winter')),
        (MID_SEASON, _('Mid season'))
    )
    field = models.ForeignKey(Field, on_delete=models.PROTECT, verbose_name=_('Field'))
    crop_type = models.ForeignKey(CropType, on_delete=models.PROTECT, verbose_name=_('Crop type'))
    season = models.CharField(choices=SEASON_CHOICES, max_length=550, verbose_name=_('Season'))
    breed = models.CharField(max_length=550, verbose_name=_('breed'))
    total_acres = models.FloatField(verbose_name=_('Total acres'))
    date_sowing = models.DateField(verbose_name=_('Date sowing'))
    date_harvesting = models.DateField(blank=True, verbose_name=_('Date harvesting'), null=True)

    class Meta:
        permissions = (
            ('can_view_crop', 'Can View Crop'),
        )

        verbose_name = _('Crop')
        verbose_name_plural = _('Crops')

    def __str__(self):
        return f"{self.crop_type}({self.field})"


class Expense(TimeStampedModel):
    SEED = "1"
    FERTILIZER = "2"
    PESTICIDES = "3"
    WATER = "4"
    ELECTRICITY_BILL = "5"
    OIL = "6"
    LABOUR = "7"
    MISC = "8"

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
    crop = models.ForeignKey(Crop, on_delete=models.PROTECT, verbose_name=_('Crop'), related_name='crop_expenses')
    expense_type = models.CharField(
        choices=EXPENSE_TYPE_CHOICES,
        max_length=255,
        verbose_name=_('Expense type')
    )
    expense_date = models.DateField(null=False, verbose_name=_('Expense date'))
    amount = models.FloatField(null=False, blank=False, verbose_name=_('Amount'))
    notes = models.TextField(null=True, verbose_name=_('Notes'))

    spent_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='expenditures', verbose_name=_('Expend by'))
    added_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='added_expenditures', verbose_name=_('Added by'))

    class Meta:
        ordering = ('-expense_date', )
        permissions = (
            ('can_view_expense', 'Can View Expense'),
        )
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')

    def __str__(self):
        return f"Rs. {self.amount}->{self.crop}({self.expense_type}) by {self.expend_by}"


class Output(TimeStampedModel):
    crop = models.ForeignKey(Crop, on_delete=models.PROTECT, verbose_name=_('Crop'), related_name='crop_outputs')
    total_mann = models.FloatField(help_text=_('Total mann weight'), verbose_name=_('Total mann'))
    rate_per_mann = models.IntegerField(help_text=_('Per mann rate'), verbose_name=_('Rate per mann'))
    sold_date = models.DateField(verbose_name=_('Sold date'))
    notes = models.CharField(max_length=550, null=True, blank=True, verbose_name=_('Notes'))

    class Meta:
        ordering = ('-sold_date', )
        permissions = (
            ('can_view_output', 'Can View Output'),
        )
        verbose_name = _('Output')
        verbose_name_plural = _('Outputs')

    def __str__(self):
        return f"Rs. {self.crop}->{self.total_mann}"
