from django.db import migrations


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


def seed_catalog(apps, schema_editor):
    ProcedimientoGastro = apps.get_model("procedimientos", "ProcedimientoGastro")
    for procedure_data in DEFAULT_PROCEDURE_CATALOG:
        ProcedimientoGastro.objects.get_or_create(
            codigo=procedure_data["codigo"],
            defaults=procedure_data,
        )


def unseed_catalog(apps, schema_editor):
    ProcedimientoGastro = apps.get_model("procedimientos", "ProcedimientoGastro")
    ProcedimientoGastro.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("procedimientos", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_catalog, unseed_catalog),
    ]