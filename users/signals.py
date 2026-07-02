from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .services import ensure_access_groups


@receiver(post_migrate)
def create_default_access_groups(sender, **kwargs):
  if sender.name != "users":
    return

  ensure_access_groups()
