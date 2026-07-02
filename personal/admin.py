from django.contrib import admin

from .models import Personal


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "rol", "colegiatura", "activo")
    list_filter = ("rol", "activo")
    search_fields = ("nombre_completo", "colegiatura")