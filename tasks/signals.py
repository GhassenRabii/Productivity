from django.conf import settings 
from django.contrib.auth.models import User, Group   
from django.dispatch import receiver
from .models import Profile
from django.db.models.signals import post_save
from django.utils import timezone
from .models import Task
from .aws_events import put_task_created

DEFAULT_GROUP_NAME = "users"

@receiver(post_save, sender=Task)
def schedule_on_create(sender, instance: Task, created, **kwargs):
    if not created:
        return
    due = getattr(instance, "due_date", None)
    owner = getattr(instance, "owner", None)  # adjust to your model
    if not (due and owner and owner.email):
        return  # nothing to schedule or no email available

    # Convert to UTC ISO with Z
    if timezone.is_naive(due):
        due = timezone.make_aware(due, timezone.get_current_timezone())
    due_utc = due.astimezone(timezone.utc).replace(microsecond=0)
    due_iso = due_utc.isoformat().replace("+00:00", "Z")

    detail = {
        "task_id": str(instance.pk),
        "owner_id": str(getattr(owner, "pk", "")),
        "owner_email": owner.email,
        "owner_name": owner.get_username(),      # or owner.get_full_name()
        "task_title": (instance.title or str(instance.pk)),
        "dueAtIso": due_iso,
    }
    try:
        put_task_created(detail)
    except Exception:
        import logging
        logging.getLogger("tasks").exception("Failed to emit TaskCreated event")


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
