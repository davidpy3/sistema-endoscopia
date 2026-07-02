from django.contrib import admin

from .models import (
    Colonoscopia,
    SegmentoColon,
    BiopsiaColonoscopia,
    DiagnosticoColonoscopia,
    SugerenciaColonoscopia,
)


class SegmentoColonInline(admin.TabularInline):
    model = SegmentoColon
    extra = 0
    fields = ("segmento", "estado", "texto")


class BiopsiaColonoscopiaInline(admin.TabularInline):
    model = BiopsiaColonoscopia
    extra = 0
    fields = ("frasco", "descripcion", "n_lesiones")


class DiagnosticoColonoscopiaInline(admin.TabularInline):
    model = DiagnosticoColonoscopia
    extra = 0
    fields = ("texto", "orden")


class SugerenciaColonoscopiaInline(admin.TabularInline):
    model = SugerenciaColonoscopia
    extra = 0
    fields = ("texto", "orden")


@admin.register(Colonoscopia)
class ColonoscopiaAdmin(admin.ModelAdmin):
    list_display = (
        "paciente",
        "fecha",
        "medico",
        "boston_total_display",
        "preparacion_adecuada_display",
        "intubacion_cecal",
    )
    list_filter = ("fecha", "medico", "intubacion_cecal", "ileoscopia_distal")
    search_fields = ("paciente__nombres", "paciente__apellidos", "paciente__dni")
    autocomplete_fields = ("paciente", "medico", "enfermera")
    date_hierarchy = "fecha"

    fieldsets = (
        ("Datos del procedimiento", {
            "fields": (
                "paciente", "medico", "enfermera", "fecha",
                "motivo", "antecedentes", "sedacion", "farmacos",
                "tiempo_retiro_min",
            )
        }),
        ("Indicadores de calidad", {
            "fields": (
                "intubacion_cecal", "foto_doc_ciego", "ileoscopia_distal",
                "boston_cd", "boston_ct", "boston_ci",
            )
        }),
        ("Inspección anal / tacto rectal", {
            "fields": ("insp_pasiva", "insp_activa", "tacto_rectal", "canal_anal")
        }),
    )

    inlines = [
        SegmentoColonInline,
        BiopsiaColonoscopiaInline,
        DiagnosticoColonoscopiaInline,
        SugerenciaColonoscopiaInline,
    ]

    @admin.display(description="Boston total")
    def boston_total_display(self, obj):
        return obj.boston_total if obj.boston_total is not None else "—"

    @admin.display(description="Prep. adecuada", boolean=True)
    def preparacion_adecuada_display(self, obj):
        return bool(obj.preparacion_adecuada)