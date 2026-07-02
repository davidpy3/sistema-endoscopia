from django.contrib.auth import authenticate
from rest_framework import serializers

from users.services import build_access_profile


class LoginSerializer(serializers.Serializer):
  username = serializers.CharField()
  password = serializers.CharField(write_only=True)

  def validate(self, attrs):
    request = self.context.get('request')
    user = authenticate(
      request=request,
      username=attrs.get('username'),
      password=attrs.get('password'),
    )
    if not user:
      raise serializers.ValidationError('Usuario o contraseña inválidos.')

    attrs['user'] = user
    return attrs


class CurrentUserSerializer(serializers.Serializer):
  id = serializers.IntegerField()
  username = serializers.CharField()
  first_name = serializers.CharField(allow_blank=True)
  last_name = serializers.CharField(allow_blank=True)
  is_superuser = serializers.BooleanField()
  is_staff = serializers.BooleanField()
  groups = serializers.ListField(child=serializers.CharField())
  access = serializers.SerializerMethodField()

  def get_access(self, obj):
    profile = build_access_profile(obj)
    return {
      'role': profile.role,
      'role_label': profile.role_label,
      'groups': profile.groups,
      'can_read': profile.can_read,
      'can_write': profile.can_write,
      'can_delete': profile.can_delete,
    }

  def to_representation(self, user):
    return {
      'id': user.id,
      'username': user.username,
      'first_name': user.first_name,
      'last_name': user.last_name,
      'is_superuser': user.is_superuser,
      'is_staff': user.is_staff,
      'groups': list(user.groups.values_list('name', flat=True)),
      'access': self.get_access(user),
    }
