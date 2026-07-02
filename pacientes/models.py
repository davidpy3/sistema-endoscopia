from django.db import models


class Paciente(models.Model):
    SEXO_CHOICES = [("M", "Masculino"), ("F", "Femenino")]

    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    dni = models.CharField(max_length=8, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.dni})"