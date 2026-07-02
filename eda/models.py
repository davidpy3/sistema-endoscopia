from django.db import models

from procedimientos.models import (
    ProcedimientoBase,
    DiagnosticoBase,
    SugerenciaBase,
    BiopsiaBase,
    ESTADO_SEGMENTO_CHOICES,
)

SEGMENTOS_EDA = [
    ("esofago", "Esófago"),
    ("fondo", "Estómago — Fondo"),
    ("cuerpo", "Estómago — Cuerpo"),
    ("angulo", "Estómago — Ángulo"),
    ("antro", "Estómago — Antro"),
    ("bulbo", "Duodeno — Bulbo"),
    ("segporcion", "Duodeno — 2.ª porción"),
]

TEXTO_NORMAL_EDA = {
    "esofago": "Mucosa de aspecto conservado. Línea Z regular, no congestiva.",
    "fondo": "Mucosa de aspecto conservado.",
    "cuerpo": "Mucosa de aspecto conservado. Pliegues gástricos sin alteraciones.",
    "angulo": "Mucosa de aspecto conservado.",
    "antro": "Mucosa de aspecto conservado.",
    "bulbo": "Mucosa de aspecto conservado.",
    "segporcion": "Mucosa de aspecto conservado. Ampolla de Vater sin alteraciones.",
}

HILL_CHOICES = [
    ("hill1", "Hill I"),
    ("hill2", "Hill II"),
    ("hill3", "Hill III"),
    ("hill4", "Hill IV"),
]

PILORO_CHOICES = [
    ("centrico", "Céntrico y permeable"),
    ("deformado", "Deformado"),
    ("estenotico", "Estenótico"),
]

PEACE_CHOICES = [(1, "1"), (2, "2"), (3, "3")]


class EDA(ProcedimientoBase):
    tiempo_examen_min = models.PositiveSmallIntegerField(null=True, blank=True)

    # Score PEACE por segmento (equivalente al Boston de colonoscopia)
    peace_esofago = models.PositiveSmallIntegerField(
        choices=PEACE_CHOICES, null=True, blank=True
    )
    peace_estomago = models.PositiveSmallIntegerField(
        choices=PEACE_CHOICES, null=True, blank=True
    )
    peace_duodeno = models.PositiveSmallIntegerField(
        choices=PEACE_CHOICES, null=True, blank=True
    )

    class Meta:
        ordering = ["-fecha"]

    @property
    def peace_total(self):
        vals = (self.peace_esofago, self.peace_estomago, self.peace_duodeno)
        if None in vals:
            return None
        return sum(vals)

    def __str__(self):
        return f"EDA — {self.paciente} — {self.fecha}"


class SegmentoEDA(models.Model):
    eda = models.ForeignKey(EDA, on_delete=models.CASCADE, related_name="segmentos")
    segmento = models.CharField(max_length=20, choices=SEGMENTOS_EDA)
    estado = models.CharField(
        max_length=10, choices=ESTADO_SEGMENTO_CHOICES, default="normal"
    )
    texto = models.TextField(blank=True)

    # Sub-campos condicionales del prototipo: solo aplican a "fondo" y "antro"
    cardias_hill = models.CharField(max_length=10, choices=HILL_CHOICES, blank=True)
    piloro = models.CharField(max_length=15, choices=PILORO_CHOICES, blank=True)

    class Meta:
        unique_together = ("eda", "segmento")
        ordering = ["eda_id", "id"]

    def save(self, *args, **kwargs):
        if self.estado == "normal" and not self.texto:
            self.texto = TEXTO_NORMAL_EDA.get(self.segmento, "")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_segmento_display()} ({self.estado})"


class BiopsiaEDA(BiopsiaBase):
    eda = models.ForeignKey(EDA, on_delete=models.CASCADE, related_name="biopsias")


class DiagnosticoEDA(DiagnosticoBase):
    eda = models.ForeignKey(EDA, on_delete=models.CASCADE, related_name="diagnosticos")


class SugerenciaEDA(SugerenciaBase):
    eda = models.ForeignKey(EDA, on_delete=models.CASCADE, related_name="sugerencias")