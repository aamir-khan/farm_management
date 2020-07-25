from modeltranslation.translator import register, TranslationOptions

from apps.farms.models import CropType


@register(CropType)
class CropTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
