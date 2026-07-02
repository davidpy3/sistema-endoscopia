from rest_framework import serializers

from .models import (
    Colonoscopia,
    SegmentoColon,
    BiopsiaColonoscopia,
    DiagnosticoColonoscopia,
    SugerenciaColonoscopia,
    TEXTO_NORMAL_COLON,
)


class SegmentoColonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SegmentoColon
        fields = ["id", "segmento", "estado", "texto"]


class BiopsiaColonoscopiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiopsiaColonoscopia
        fields = ["id", "frasco", "descripcion", "n_lesiones"]


class DiagnosticoColonoscopiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticoColonoscopia
        fields = ["id", "texto", "orden"]


class SugerenciaColonoscopiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SugerenciaColonoscopia
        fields = ["id", "texto", "orden"]


class ColonoscopiaSerializer(serializers.ModelSerializer):
    # Repetidores del prototipo, anidados y escribibles
    segmentos = SegmentoColonSerializer(many=True, required=False)
    biopsias = BiopsiaColonoscopiaSerializer(many=True, required=False)
    diagnosticos = DiagnosticoColonoscopiaSerializer(many=True, required=False)
    sugerencias = SugerenciaColonoscopiaSerializer(many=True, required=False)

    # Calculados (equivalen a qb_boston / q_prep_auto del JS)
    boston_total = serializers.ReadOnlyField()
    preparacion_adecuada = serializers.ReadOnlyField()

    paciente_nombre = serializers.CharField(source="paciente.__str__", read_only=True)
    medico_nombre = serializers.CharField(source="medico.__str__", read_only=True)

    class Meta:
        model = Colonoscopia
        fields = [
            "id",
            "paciente", "paciente_nombre",
            "medico", "medico_nombre",
            "enfermera",
            "fecha", "motivo", "antecedentes", "sedacion", "farmacos",
            "tiempo_retiro_min",
            "intubacion_cecal", "foto_doc_ciego", "ileoscopia_distal",
            "boston_cd", "boston_ct", "boston_ci",
            "boston_total", "preparacion_adecuada",
            "insp_pasiva", "insp_activa", "tacto_rectal", "canal_anal",
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

        colonoscopia = Colonoscopia.objects.create(**validated_data)

        self._sync_segmentos(colonoscopia, segmentos_data)
        for data in biopsias_data:
            BiopsiaColonoscopia.objects.create(colonoscopia=colonoscopia, **data)
        for data in diagnosticos_data:
            DiagnosticoColonoscopia.objects.create(colonoscopia=colonoscopia, **data)
        for data in sugerencias_data:
            SugerenciaColonoscopia.objects.create(colonoscopia=colonoscopia, **data)

        return colonoscopia

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

        # Repetidores libres (dx/sugerencias/biopsias): se reemplazan completos,
        # igual que el prototipo hace con readRepeater() al guardar el caso.
        if biopsias_data is not None:
            instance.biopsias.all().delete()
            for data in biopsias_data:
                BiopsiaColonoscopia.objects.create(colonoscopia=instance, **data)
        if diagnosticos_data is not None:
            instance.diagnosticos.all().delete()
            for data in diagnosticos_data:
                DiagnosticoColonoscopia.objects.create(colonoscopia=instance, **data)
        if sugerencias_data is not None:
            instance.sugerencias.all().delete()
            for data in sugerencias_data:
                SugerenciaColonoscopia.objects.create(colonoscopia=instance, **data)

        return instance

    def _sync_segmentos(self, colonoscopia, segmentos_data):
        """Los 6 segmentos son fijos (unique_together colonoscopia+segmento),
        así que se hace upsert en vez de borrar/recrear."""
        for data in segmentos_data:
            segmento = data["segmento"]
            estado = data.get("estado", "normal")
            texto = data.get("texto", "")
            segmento_actual = SegmentoColon.objects.filter(
                colonoscopia=colonoscopia,
                segmento=segmento,
            ).first()

            if estado == "normal":
                if segmento_actual is None or segmento_actual.estado != "normal" or not texto:
                    texto = TEXTO_NORMAL_COLON.get(segmento, "")

            SegmentoColon.objects.update_or_create(
                colonoscopia=colonoscopia,
                segmento=segmento,
                defaults={
                    "estado": estado,
                    "texto": texto,
                },
            )