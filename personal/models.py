from django.db import models


class Personal(models.Model):
    ROL_CHOICES = [
        ("medico", "Médico endoscopista"),
        ("enfermera", "Enfermera asistente"),
    ]

    nombre_completo = models.CharField(max_length=200)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    colegiatura = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre_completo"]

    def __str__(self):
        return f"{self.nombre_completo} ({self.get_rol_display()})"