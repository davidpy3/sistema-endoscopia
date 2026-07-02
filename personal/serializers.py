from rest_framework import serializers

from .models import Personal


class PersonalSerializer(serializers.ModelSerializer):
    rol_display = serializers.CharField(source="get_rol_display", read_only=True)

    class Meta:
        model = Personal
        fields = ["id", "nombre_completo", "rol", "rol_display", "colegiatura", "activo"]