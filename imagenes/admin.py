from django.contrib import admin

from .models import ImagenEndoscopica


@admin.register(ImagenEndoscopica)
class ImagenEndoscopicaAdmin(admin.ModelAdmin):
    list_display = ("epigrafe", "content_type", "object_id", "orden", "subido_en")
    list_filter = ("content_type",)
    search_fields = ("epigrafe",)