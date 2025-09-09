from django.conf import settings 
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group   
from django.dispatch import receiver
from .models import Profile

DEFAULT_GROUP_NAME = "users"

@receiver(post_save, sender=User)
def add_user_to_default_group(sender, instance, created, **kwargs):
    if not created:
        return
    group, _ = Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    instance.groups.add(group)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    # Only if you have extra fields that mirror user fields
    if hasattr(instance, "profile"):
        instance.profile.save()
