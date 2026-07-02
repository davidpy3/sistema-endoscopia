from django.db import models

from procedimientos.models import (
    ProcedimientoBase,
    DiagnosticoBase,
    SugerenciaBase,
    BiopsiaBase,
    ESTADO_SEGMENTO_CHOICES,
)

SEGMENTOS_COLON = [
    ("ciego", "Ciego"),
    ("ascendente", "Colon ascendente"),
    ("transverso", "Colon transverso"),
    ("descendente", "Colon descendente"),
    ("sigmoides", "Colon sigmoides"),
    ("recto", "Recto"),
]

# Frase estándar cuando el segmento está "Normal" (igual al array ORGANS del prototipo JS)
TEXTO_NORMAL_COLON = {
    "ciego": (
        "Se visualiza orificio apendicular y válvula ileocecal de aspecto "
        "conservado. Mucosa y patrón vascular submucoso de aspecto conservado."
    ),
    "ascendente": "Mucosa y patrón vascular submucoso de aspecto conservado.",
    "transverso": "Mucosa y patrón vascular submucoso de aspecto conservado.",
    "descendente": "Mucosa y patrón vascular submucoso de aspecto conservado.",
    "sigmoides": "Mucosa y patrón vascular submucoso de aspecto conservado.",
    "recto": "Mucosa y patrón vascular submucoso de aspecto conservado.",
}


class Colonoscopia(ProcedimientoBase):
    tiempo_retiro_min = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )

    # 2. Indicadores de calidad
    intubacion_cecal = models.BooleanField(null=True, blank=True)
    foto_doc_ciego = models.BooleanField(null=True, blank=True)
    ileoscopia_distal = models.BooleanField(null=True, blank=True)
    boston_cd = models.PositiveSmallIntegerField(null=True, blank=True)  # colon derecho
    boston_ct = models.PositiveSmallIntegerField(null=True, blank=True)  # transverso
    boston_ci = models.PositiveSmallIntegerField(null=True, blank=True)  # izquierdo

    # 3. Inspección anal / tacto rectal
    insp_pasiva = models.CharField(max_length=300, blank=True)
    insp_activa = models.CharField(max_length=300, blank=True)
    tacto_rectal = models.CharField(max_length=300, blank=True)
    canal_anal = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-fecha"]

    @property
    def boston_total(self):
        vals = (self.boston_cd, self.boston_ct, self.boston_ci)
        if None in vals:
            return None
        return sum(vals)

    @property
    def preparacion_adecuada(self):
        """Replica la lógica de recalcQuality() del prototipo:
        total >= 6 Y cada segmento >= 2."""
        vals = (self.boston_cd, self.boston_ct, self.boston_ci)
        if None in vals:
            return None
        total = sum(vals)
        return total >= 6 and all(v >= 2 for v in vals)

    def __str__(self):
        return f"Colonoscopía — {self.paciente} — {self.fecha}"


class SegmentoColon(models.Model):
    colonoscopia = models.ForeignKey(
        Colonoscopia, on_delete=models.CASCADE, related_name="segmentos"
    )
    segmento = models.CharField(max_length=20, choices=SEGMENTOS_COLON)
    estado = models.CharField(
        max_length=10, choices=ESTADO_SEGMENTO_CHOICES, default="normal"
    )
    texto = models.TextField(blank=True)

    class Meta:
        unique_together = ("colonoscopia", "segmento")
        ordering = ["colonoscopia_id", "id"]

    def save(self, *args, **kwargs):
        # Si está "normal" y no se tocó el texto, autocompleta como hace el JS
        if self.estado == "normal" and not self.texto:
            self.texto = TEXTO_NORMAL_COLON.get(self.segmento, "")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_segmento_display()} ({self.estado})"


class BiopsiaColonoscopia(BiopsiaBase):
    colonoscopia = models.ForeignKey(
        Colonoscopia, on_delete=models.CASCADE, related_name="biopsias"
    )


class DiagnosticoColonoscopia(DiagnosticoBase):
    colonoscopia = models.ForeignKey(
        Colonoscopia, on_delete=models.CASCADE, related_name="diagnosticos"
    )


class SugerenciaColonoscopia(SugerenciaBase):
    colonoscopia = models.ForeignKey(
        Colonoscopia, on_delete=models.CASCADE, related_name="sugerencias"
    )
