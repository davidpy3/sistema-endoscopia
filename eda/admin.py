from django.contrib import admin

from .models import (
    EDA,
    SegmentoEDA,
    BiopsiaEDA,
    DiagnosticoEDA,
    SugerenciaEDA,
)


class SegmentoEDAInline(admin.TabularInline):
    model = SegmentoEDA
    extra = 0
    fields = ("segmento", "estado", "texto", "cardias_hill", "piloro")


class BiopsiaEDAInline(admin.TabularInline):
    model = BiopsiaEDA
    extra = 0
    fields = ("frasco", "descripcion", "n_lesiones")


class DiagnosticoEDAInline(admin.TabularInline):
    model = DiagnosticoEDA
    extra = 0
    fields = ("texto", "orden")


class SugerenciaEDAInline(admin.TabularInline):
    model = SugerenciaEDA
    extra = 0
    fields = ("texto", "orden")


@admin.register(EDA)
class EDAAdmin(admin.ModelAdmin):
    list_display = ("paciente", "fecha", "medico", "peace_total_display", "tiempo_examen_min")
    list_filter = ("fecha", "medico")
    search_fields = ("paciente__nombres", "paciente__apellidos", "paciente__dni")
    autocomplete_fields = ("paciente", "medico", "enfermera")
    date_hierarchy = "fecha"

    fieldsets = (
        ("Datos del procedimiento", {
            "fields": (
                "paciente", "medico", "enfermera", "fecha",
                "motivo", "antecedentes", "sedacion", "farmacos",
                "tiempo_examen_min",
            )
        }),
        ("Score PEACE", {
            "fields": ("peace_esofago", "peace_estomago", "peace_duodeno")
        }),
    )

    inlines = [SegmentoEDAInline, BiopsiaEDAInline, DiagnosticoEDAInline, SugerenciaEDAInline]

    @admin.display(description="PEACE total")
    def peace_total_display(self, obj):
        return obj.peace_total if obj.peace_total is not None else "—"