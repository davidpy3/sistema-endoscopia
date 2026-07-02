from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ImagenEndoscopica(models.Model):
    """Equivale a la galería del prototipo (drag&drop + epígrafe).
    Usa GenericForeignKey para servir tanto a EDA como a Colonoscopia
    sin duplicar el modelo."""

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("eda", "colonoscopia")},
    )
    object_id = models.PositiveIntegerField()
    procedimiento = GenericForeignKey("content_type", "object_id")

    archivo = models.ImageField(upload_to="endoscopia/%Y/%m/")
    epigrafe = models.CharField(max_length=200, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    subido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["content_type", "object_id", "orden"]

    def __str__(self):
        return self.epigrafe or f"Imagen #{self.pk}"