#!/usr/bin/env python
"""Seed de desarrollo para SQLite con datos clínicos simulados."""

from __future__ import annotations

import os
import shutil
from datetime import date
from io import BytesIO
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.management import call_command
from PIL import Image

from pacientes.models import Paciente
from personal.models import Personal
from colonoscopia.models import (
    Colonoscopia,
    SegmentoColon,
    BiopsiaColonoscopia,
    DiagnosticoColonoscopia,
    SugerenciaColonoscopia,
)
from eda.models import (
    EDA,
    SegmentoEDA,
    BiopsiaEDA,
    DiagnosticoEDA,
    SugerenciaEDA,
)
from imagenes.models import ImagenEndoscopica


def build_png(label: str, color: tuple[int, int, int]) -> ContentFile:
    image = Image.new("RGB", (900, 600), color=color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"{label}.png")


def main() -> None:
    call_command("migrate", interactive=False, verbosity=0)

    ImagenEndoscopica.objects.all().delete()
    for model in [
        BiopsiaColonoscopia,
        DiagnosticoColonoscopia,
        SugerenciaColonoscopia,
        SegmentoColon,
        Colonoscopia,
        BiopsiaEDA,
        DiagnosticoEDA,
        SugerenciaEDA,
        SegmentoEDA,
        EDA,
        Paciente,
        Personal,
    ]:
        model.objects.all().delete()

    media_demo = Path(settings.MEDIA_ROOT) / "endoscopia"
    shutil.rmtree(media_demo, ignore_errors=True)
    media_demo.mkdir(parents=True, exist_ok=True)

    User = get_user_model()
    demo_user, _ = User.objects.get_or_create(
        username="demo",
        defaults={
            "first_name": "Demo",
            "last_name": "Endoscopia",
            "email": "demo@example.com",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )
    demo_user.first_name = "Demo"
    demo_user.last_name = "Endoscopia"
    demo_user.email = "demo@example.com"
    demo_user.is_staff = True
    demo_user.is_superuser = True
    demo_user.is_active = True
    demo_user.set_password("demo1234")
    demo_user.save()

    pacientes = [
        Paciente.objects.create(
            nombres="María Elena",
            apellidos="Quispe Rojas",
            dni="71234567",
            fecha_nacimiento=date(1982, 5, 14),
            sexo="F",
            telefono="985-111-222",
        ),
        Paciente.objects.create(
            nombres="Carlos Alberto",
            apellidos="Vargas Paredes",
            dni="84561239",
            fecha_nacimiento=date(1975, 11, 2),
            sexo="M",
            telefono="976-333-444",
        ),
        Paciente.objects.create(
            nombres="Lucía Fernanda",
            apellidos="Soto Medina",
            dni="90345678",
            fecha_nacimiento=date(1991, 8, 27),
            sexo="F",
            telefono="912-555-666",
        ),
    ]

    personal = [
        Personal.objects.create(
            nombre_completo="Dr. José Luis Mendoza",
            rol="medico",
            colegiatura="CMP 44122",
            activo=True,
        ),
        Personal.objects.create(
            nombre_completo="Dra. Ana Patricia Ríos",
            rol="medico",
            colegiatura="CMP 55881",
            activo=True,
        ),
        Personal.objects.create(
            nombre_completo="Enf. Rosa Castillo",
            rol="enfermera",
            colegiatura="ENF 23881",
            activo=True,
        ),
        Personal.objects.create(
            nombre_completo="Enf. Miguel Huamán",
            rol="enfermera",
            colegiatura="ENF 11442",
            activo=True,
        ),
    ]

    medico_1, medico_2 = personal[0], personal[1]
    enfermera_1, enfermera_2 = personal[2], personal[3]

    colon_1 = Colonoscopia.objects.create(
        paciente=pacientes[0],
        medico=medico_1,
        enfermera=enfermera_1,
        fecha=date(2026, 6, 18),
        motivo="Sangrado digestivo bajo intermitente y control de pólipos previos.",
        antecedentes="Antecedente familiar de cáncer colorrectal. Colonoscopía previa hace 4 años.",
        sedacion="consciente",
        farmacos="Midazolam + propofol titulado",
        tiempo_retiro_min=9.5,
        intubacion_cecal=True,
        foto_doc_ciego=True,
        ileoscopia_distal=False,
        boston_cd=2,
        boston_ct=2,
        boston_ci=1,
        insp_pasiva="Sin lesiones externas visibles.",
        insp_activa="Sin cambios significativos con pujo.",
        tacto_rectal="Canal anal sin masas palpables.",
        canal_anal="Normotónico.",
        creado_por=demo_user,
    )

    colon_1_segments = {
        "ciego": ("normal", ""),
        "ascendente": ("normal", ""),
        "transverso": ("normal", ""),
        "descendente": ("alterado", "Mucosa con leve congestión focal y pequeña erosión superficial."),
        "sigmoides": ("alterado", "Diverticulosis múltiple sin estigmas de sangrado."),
        "recto": ("normal", ""),
    }
    for key, (estado, texto) in colon_1_segments.items():
        SegmentoColon.objects.update_or_create(
            colonoscopia=colon_1,
            segmento=key,
            defaults={"estado": estado, "texto": texto},
        )

    BiopsiaColonoscopia.objects.create(
        colonoscopia=colon_1,
        frasco="A1",
        descripcion="Biopsia de mucosa en descendente",
        n_lesiones=1,
    )
    BiopsiaColonoscopia.objects.create(
        colonoscopia=colon_1,
        frasco="A2",
        descripcion="Muestra de lesión en sigmoides",
        n_lesiones=2,
    )
    DiagnosticoColonoscopia.objects.create(
        colonoscopia=colon_1,
        texto="Diverticulosis colónica no complicada.",
        orden=0,
    )
    DiagnosticoColonoscopia.objects.create(
        colonoscopia=colon_1,
        texto="Erosiones focales en colon descendente.",
        orden=1,
    )
    SugerenciaColonoscopia.objects.create(
        colonoscopia=colon_1,
        texto="Control clínico y dieta rica en fibra.",
        orden=0,
    )
    SugerenciaColonoscopia.objects.create(
        colonoscopia=colon_1,
        texto="Retomar control endoscópico según anatomía patológica.",
        orden=1,
    )

    colon_2 = Colonoscopia.objects.create(
        paciente=pacientes[1],
        medico=medico_2,
        enfermera=enfermera_2,
        fecha=date(2026, 6, 25),
        motivo="Tamizaje por edad y antecedente de anemia ferropénica.",
        antecedentes="Sin procedimientos previos relevantes.",
        sedacion="profunda",
        farmacos="Propofol",
        tiempo_retiro_min=12,
        intubacion_cecal=True,
        foto_doc_ciego=True,
        ileoscopia_distal=True,
        boston_cd=3,
        boston_ct=3,
        boston_ci=3,
        insp_pasiva="Inspección anal sin hallazgos patológicos.",
        insp_activa="Sin prolapsos ni sangrado.",
        tacto_rectal="Sin dolor ni masas.",
        canal_anal="Adecuado.",
        creado_por=demo_user,
    )

    for key in ["ciego", "ascendente", "transverso", "descendente", "sigmoides", "recto"]:
        SegmentoColon.objects.update_or_create(
            colonoscopia=colon_2,
            segmento=key,
            defaults={"estado": "normal", "texto": ""},
        )

    BiopsiaColonoscopia.objects.create(
        colonoscopia=colon_2,
        frasco="B1",
        descripcion="Biopsia de pólipo diminuto en recto",
        n_lesiones=1,
    )
    DiagnosticoColonoscopia.objects.create(
        colonoscopia=colon_2,
        texto="Examen sin lesiones significativas.",
        orden=0,
    )
    SugerenciaColonoscopia.objects.create(
        colonoscopia=colon_2,
        texto="Control preventivo según hallazgos histológicos.",
        orden=0,
    )

    eda_1 = EDA.objects.create(
        paciente=pacientes[2],
        medico=medico_1,
        enfermera=enfermera_2,
        fecha=date(2026, 6, 20),
        motivo="Dispepsia y pirosis de varios meses de evolución.",
        antecedentes="Uso ocasional de AINEs.",
        sedacion="consciente",
        farmacos="Midazolam",
        tiempo_examen_min=7,
        peace_esofago=2,
        peace_estomago=3,
        peace_duodeno=2,
        creado_por=demo_user,
    )

    eda_1_segments = {
        "esofago": ("normal", "", "", ""),
        "fondo": ("alterado", "Plegues gástricos discretamente engrosados.", "hill2", ""),
        "cuerpo": ("normal", "", "", ""),
        "angulo": ("normal", "", "", ""),
        "antro": ("alterado", "Eritema antral leve, sin erosiones.", "", "centrico"),
        "bulbo": ("normal", "", "", ""),
        "segporcion": ("normal", "", "", ""),
    }
    for key, (estado, texto, hill, piloro) in eda_1_segments.items():
        SegmentoEDA.objects.update_or_create(
            eda=eda_1,
            segmento=key,
            defaults={
                "estado": estado,
                "texto": texto,
                "cardias_hill": hill,
                "piloro": piloro,
            },
        )

    BiopsiaEDA.objects.create(eda=eda_1, frasco="C1", descripcion="Biopsia antral por gastritis", n_lesiones=1)
    BiopsiaEDA.objects.create(eda=eda_1, frasco="C2", descripcion="Biopsia de esófago distal", n_lesiones=1)
    DiagnosticoEDA.objects.create(eda=eda_1, texto="Gastritis antral leve.", orden=0)
    DiagnosticoEDA.objects.create(eda=eda_1, texto="Reflujo gastroesofágico no erosivo.", orden=1)
    SugerenciaEDA.objects.create(eda=eda_1, texto="Higiene dietética y control con gastroenterología.", orden=0)
    SugerenciaEDA.objects.create(eda=eda_1, texto="Esperar anatomía patológica si corresponde.", orden=1)

    eda_2 = EDA.objects.create(
        paciente=pacientes[0],
        medico=medico_2,
        enfermera=enfermera_1,
        fecha=date(2026, 6, 28),
        motivo="Dolor epigástrico y náuseas postprandiales.",
        antecedentes="Sin cirugía previa.",
        sedacion="naap",
        farmacos="Propofol",
        tiempo_examen_min=6,
        peace_esofago=3,
        peace_estomago=3,
        peace_duodeno=3,
        creado_por=demo_user,
    )

    for key in ["esofago", "fondo", "cuerpo", "angulo", "antro", "bulbo", "segporcion"]:
        SegmentoEDA.objects.update_or_create(
            eda=eda_2,
            segmento=key,
            defaults={"estado": "normal", "texto": ""},
        )

    BiopsiaEDA.objects.create(eda=eda_2, frasco="D1", descripcion="Sin biopsias", n_lesiones=None)
    DiagnosticoEDA.objects.create(eda=eda_2, texto="Endoscopía alta sin alteraciones macroscópicas.", orden=0)
    SugerenciaEDA.objects.create(eda=eda_2, texto="Seguimiento clínico.", orden=0)

    ct_colon = ContentType.objects.get_for_model(Colonoscopia)
    ct_eda = ContentType.objects.get_for_model(EDA)

    sample_images = [
        (ct_colon, colon_1, "colon-1", "Colonoscopía descendente", (22, 104, 128), 0),
        (ct_colon, colon_2, "colon-2", "Colonoscopía normal", (58, 142, 114), 1),
        (ct_eda, eda_1, "eda-1", "EDA fondo/antro", (162, 114, 59), 0),
        (ct_eda, eda_2, "eda-2", "EDA normal", (86, 95, 145), 1),
    ]

    for content_type, obj, label, epigrafe, color, orden in sample_images:
        ImagenEndoscopica.objects.create(
            content_type=content_type,
            object_id=obj.id,
            archivo=build_png(label, color),
            epigrafe=epigrafe,
            orden=orden,
        )

    print("Seed completado")
    print("Usuario demo: demo / demo1234")
    print(f"Pacientes: {Paciente.objects.count()}")
    print(f"Personal: {Personal.objects.count()}")
    print(f"Colonoscopías: {Colonoscopia.objects.count()}")
    print(f"EDA: {EDA.objects.count()}")
    print(f"Imágenes: {ImagenEndoscopica.objects.count()}")


if __name__ == "__main__":
    main()