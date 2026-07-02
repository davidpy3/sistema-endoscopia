from django.contrib import admin

from .models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("apellidos", "nombres", "dni", "sexo", "fecha_nacimiento", "telefono")
    search_fields = ("apellidos", "nombres", "dni")
    list_filter = ("sexo",)