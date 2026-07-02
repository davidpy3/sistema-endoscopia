from rest_framework import serializers

from .models import (
    EDA,
    SegmentoEDA,
    BiopsiaEDA,
    DiagnosticoEDA,
    SugerenciaEDA,
)


class SegmentoEDASerializer(serializers.ModelSerializer):
    class Meta:
        model = SegmentoEDA
        fields = ["id", "segmento", "estado", "texto", "cardias_hill", "piloro"]


class BiopsiaEDASerializer(serializers.ModelSerializer):
    class Meta:
        model = BiopsiaEDA
        fields = ["id", "frasco", "descripcion", "n_lesiones"]


class DiagnosticoEDASerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticoEDA
        fields = ["id", "texto", "orden"]


class SugerenciaEDASerializer(serializers.ModelSerializer):
    class Meta:
        model = SugerenciaEDA
        fields = ["id", "texto", "orden"]


class EDASerializer(serializers.ModelSerializer):
    segmentos = SegmentoEDASerializer(many=True, required=False)
    biopsias = BiopsiaEDASerializer(many=True, required=False)
    diagnosticos = DiagnosticoEDASerializer(many=True, required=False)
    sugerencias = SugerenciaEDASerializer(many=True, required=False)

    peace_total = serializers.ReadOnlyField()

    paciente_nombre = serializers.CharField(source="paciente.__str__", read_only=True)
    medico_nombre = serializers.CharField(source="medico.__str__", read_only=True)

    class Meta:
        model = EDA
        fields = [
            "id",
            "paciente", "paciente_nombre",
            "medico", "medico_nombre",
            "enfermera",
            "fecha", "motivo", "antecedentes", "sedacion", "farmacos",
            "tiempo_examen_min",
            "peace_esofago", "peace_estomago", "peace_duodeno", "peace_total",
            "segmentos", "biopsias", "diagnosticos", "sugerencias",
            "creado_en", "actualizado_en",
        ]
        read_only_fields = ["creado_en", "actualizado_en"]

    def create(self, validated_data):
        segmentos_data = validated_data.pop("segmentos", [])
        biopsias_data = validated_data.pop("biopsias", [])
        diagnosticos_data = validated_data.pop("diagnosticos", [])
        sugerencias_data = validated_data.pop("sugerencias", [])

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["creado_por"] = request.user

        eda = EDA.objects.create(**validated_data)

        self._sync_segmentos(eda, segmentos_data)
        for data in biopsias_data:
            BiopsiaEDA.objects.create(eda=eda, **data)
        for data in diagnosticos_data:
            DiagnosticoEDA.objects.create(eda=eda, **data)
        for data in sugerencias_data:
            SugerenciaEDA.objects.create(eda=eda, **data)

        return eda

    def update(self, instance, validated_data):
        segmentos_data = validated_data.pop("segmentos", None)
        biopsias_data = validated_data.pop("biopsias", None)
        diagnosticos_data = validated_data.pop("diagnosticos", None)
        sugerencias_data = validated_data.pop("sugerencias", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if segmentos_data is not None:
            self._sync_segmentos(instance, segmentos_data)
        if biopsias_data is not None:
            instance.biopsias.all().delete()
            for data in biopsias_data:
                BiopsiaEDA.objects.create(eda=instance, **data)
        if diagnosticos_data is not None:
            instance.diagnosticos.all().delete()
            for data in diagnosticos_data:
                DiagnosticoEDA.objects.create(eda=instance, **data)
        if sugerencias_data is not None:
            instance.sugerencias.all().delete()
            for data in sugerencias_data:
                SugerenciaEDA.objects.create(eda=instance, **data)

        return instance

    def _sync_segmentos(self, eda, segmentos_data):
        for data in segmentos_data:
            SegmentoEDA.objects.update_or_create(
                eda=eda,
                segmento=data["segmento"],
                defaults={
                    "estado": data.get("estado", "normal"),
                    "texto": data.get("texto", ""),
                    "cardias_hill": data.get("cardias_hill", ""),
                    "piloro": data.get("piloro", ""),
                },
            )