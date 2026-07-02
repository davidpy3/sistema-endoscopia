from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.models import Group

READ_GROUP = "leer"
WRITE_GROUP = "escribir"
ALL_GROUP = "todo"
ACCESS_GROUPS = (READ_GROUP, WRITE_GROUP, ALL_GROUP)
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


@dataclass(frozen=True)
class AccessProfile:
  role: str
  role_label: str
  groups: list[str]
  can_read: bool
  can_write: bool
  can_delete: bool


def ensure_access_groups() -> None:
  for group_name in ACCESS_GROUPS:
    Group.objects.get_or_create(name=group_name)


def _normalized_groups(user) -> set[str]:
  if not user.is_authenticated:
    return set()

  return {group.name.strip().lower() for group in user.groups.all()}


def get_user_role(user) -> str:
  if not user.is_authenticated:
    return "anon"

  if user.is_superuser:
    return ALL_GROUP

  groups = _normalized_groups(user)
  if ALL_GROUP in groups:
    return ALL_GROUP
  if WRITE_GROUP in groups:
    return WRITE_GROUP
  if READ_GROUP in groups:
    return READ_GROUP
  return "sin_acceso"


def get_role_label(role: str) -> str:
  labels = {
    READ_GROUP: "Lectura",
    WRITE_GROUP: "Escritura",
    ALL_GROUP: "Total",
    "sin_acceso": "Sin acceso",
    "anon": "Sin sesión",
  }
  return labels.get(role, "Sin acceso")


def can_read(user) -> bool:
  if not user.is_authenticated:
    return False

  if user.is_superuser:
    return True

  groups = _normalized_groups(user)
  return bool(groups & {READ_GROUP, WRITE_GROUP, ALL_GROUP})


def can_write(user) -> bool:
  if not user.is_authenticated:
    return False

  if user.is_superuser:
    return True

  groups = _normalized_groups(user)
  return bool(groups & {WRITE_GROUP, ALL_GROUP})


def can_delete(user) -> bool:
  if not user.is_authenticated:
    return False

  if user.is_superuser:
    return True

  groups = _normalized_groups(user)
  return ALL_GROUP in groups


def build_access_profile(user) -> AccessProfile:
  role = get_user_role(user)
  groups = sorted(_normalized_groups(user)) if user.is_authenticated else []
  return AccessProfile(
    role=role,
    role_label=get_role_label(role),
    groups=groups,
    can_read=can_read(user),
    can_write=can_write(user),
    can_delete=can_delete(user),
  )
