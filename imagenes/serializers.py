from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import ImagenEndoscopica

TIPO_CHOICES = [("eda", "EDA"), ("colonoscopia", "Colonoscopia")]


class ImagenEndoscopicaSerializer(serializers.ModelSerializer):
    # El cliente manda "eda" o "colonoscopia" + object_id, no el content_type crudo
    tipo = serializers.ChoiceField(choices=TIPO_CHOICES, write_only=True)
    tipo_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ImagenEndoscopica
        fields = [
            "id", "tipo", "tipo_display", "object_id",
            "archivo", "epigrafe", "orden", "subido_en",
        ]
        read_only_fields = ["subido_en"]

    def get_tipo_display(self, obj):
        return obj.content_type.model

    def create(self, validated_data):
        tipo = validated_data.pop("tipo")
        validated_data["content_type"] = ContentType.objects.get(
            app_label=tipo, model=tipo
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        tipo = validated_data.pop("tipo", None)
        if tipo:
            validated_data["content_type"] = ContentType.objects.get(
                app_label=tipo, model=tipo
            )
        return super().update(instance, validated_data)