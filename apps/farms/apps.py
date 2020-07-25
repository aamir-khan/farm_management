from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FarmConfig(AppConfig):
    name = 'apps.farms'
    verbose_name = _("Farms")
