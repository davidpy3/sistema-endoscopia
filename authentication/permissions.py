from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.services import can_delete, can_read, can_write


class RoleBasedAccessPermission(BasePermission):
  message = "No tiene permisos para realizar esta acción."

  def has_permission(self, request, view):
    user = request.user
    if not user or not user.is_authenticated:
      return False

    if user.is_superuser:
      return True

    if request.method in SAFE_METHODS:
      return can_read(user)
    if request.method in {"POST", "PUT", "PATCH"}:
      return can_write(user)
    if request.method == "DELETE":
      return can_delete(user)
    return False


class SuperuserWritePermission(BasePermission):
  message = "Solo el superadministrador puede modificar este recurso."

  def has_permission(self, request, view):
    user = request.user
    if not user or not user.is_authenticated:
      return False

    if user.is_superuser:
      return True

    if request.method in SAFE_METHODS:
      return can_read(user)

    return False
