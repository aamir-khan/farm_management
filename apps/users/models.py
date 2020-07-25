from django.contrib.auth.models import Permission, AbstractUser
from django.db.models.signals import post_migrate
from django.contrib.contenttypes.models import ContentType


class User(AbstractUser):
    # profile_pic = models.FileField()

    class Meta:
        verbose_name = 'Owner'
        verbose_name_plural = 'Owners'
        permissions = (
            ('can_view_userProfile', 'Can View UserProfile'),
        )

    def __str__(self):
        return self.get_full_name()


def add_view_only_permission(sender, **kwargs):
    """This creates a view only permission for sender"""
    for content_type in ContentType.objects.all():
        codename = 'can_view_%s' % content_type.model
        name = 'Can View %s' % content_type.name
        if not Permission.objects.filter(
                content_type=content_type,
                codename=codename):
            Permission.objects.create(
                content_type=content_type,
                codename=codename,
                name=name)


post_migrate.connect(add_view_only_permission)
