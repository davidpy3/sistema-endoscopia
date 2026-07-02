from django.conf import settings
from django.db import models

# Ojo: ajusta el import según dónde termines poniendo estas apps
from pacientes.models import Paciente
from personal.models import Personal

SEDACION_CHOICES = [
    ("ninguna", "Ninguna"),
    ("consciente", "Consciente"),
    ("profunda", "Profunda"),
    ("naap", "NAAP / propofol"),
]

ESTADO_SEGMENTO_CHOICES = [
    ("normal", "Normal"),
    ("alterado", "Alterado"),
]

DEFAULT_PROCEDURE_CATALOG = [
    {
        "codigo": "endoscopia",
        "nombre": "Endoscopia digestiva alta",
        "descripcion": "Valoración diagnóstica y terapéutica de esófago, estómago y duodeno.",
        "alcance": "Diagnóstico y tratamiento endoscópico",
        "orden": 0,
    },
    {
        "codigo": "colonoscopia",
        "nombre": "Colonoscopía",
        "descripcion": "Estudio completo de colon y recto con toma de biopsias y resección de lesiones.",
        "alcance": "Diagnóstico, vigilancia y terapéutica",
        "orden": 1,
    },
    {
        "codigo": "laparoscopia",
        "nombre": "Laparoscopía diagnóstica",
        "descripcion": "Abordaje mínimamente invasivo para exploración abdominal y toma de muestras.",
        "alcance": "Diagnóstico quirúrgico mínimamente invasivo",
        "orden": 2,
    },
    {
        "codigo": "cpre",
        "nombre": "CPRE",
        "descripcion": "Procedimiento endoscópico para vía biliar y pancreática con fines diagnósticos o terapéuticos.",
        "alcance": "Endoscopia terapéutica avanzada",
        "orden": 3,
    },
    {
        "codigo": "otros",
        "nombre": "Otros procedimientos gastroenterológicos",
        "descripcion": "Polipectomía, hemostasia endoscópica, colocación de clips, extracción de cuerpos extraños y más.",
        "alcance": "Apoyo diagnóstico y terapéutico",
        "orden": 4,
    },
]


class ProcedimientoGastro(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=255)
    alcance = models.CharField(max_length=120)
    orden = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["orden", "id"]

    def __str__(self):
        return self.nombre


class ProcedimientoBase(models.Model):
    """Campos comunes a la sección '1. Datos del paciente y del procedimiento'
    de ambos prototipos (EDA y Colonoscopia)."""

    paciente = models.ForeignKey(
        Paciente, on_delete=models.PROTECT, related_name="%(class)ss"
    )
    medico = models.ForeignKey(
        Personal,
        on_delete=models.PROTECT,
        related_name="%(class)ss_como_medico",
        limit_choices_to={"rol": "medico"},
    )
    enfermera = models.ForeignKey(
        Personal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)ss_como_enfermera",
        limit_choices_to={"rol": "enfermera"},
    )
    fecha = models.DateField()
    motivo = models.TextField(blank=True)
    antecedentes = models.TextField(blank=True)
    sedacion = models.CharField(max_length=20, choices=SEDACION_CHOICES, blank=True)
    farmacos = models.CharField(max_length=200, blank=True)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)ss_creados",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DiagnosticoBase(models.Model):
    """Repetidor de texto libre (sección Diagnósticos en ambos prototipos)."""

    texto = models.CharField(max_length=500)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["orden", "id"]


class SugerenciaBase(models.Model):
    """Repetidor de texto libre (sección Sugerencias/plan)."""

    texto = models.CharField(max_length=500)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["orden", "id"]


class BiopsiaBase(models.Model):
    """Repetidor frasco/descripción/n.º lesiones (sección Biopsias)."""

    frasco = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=300)
    n_lesiones = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True