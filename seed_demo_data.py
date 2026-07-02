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
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.management import call_command
from PIL import Image

from pacientes.models import Paciente
from personal.models import Personal
from procedimientos.models import DEFAULT_PROCEDURE_CATALOG, ProcedimientoGastro
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
from users.services import ensure_access_groups, READ_GROUP, WRITE_GROUP, ALL_GROUP


def build_png(label: str, color: tuple[int, int, int]) -> ContentFile:
    image = Image.new("RGB", (900, 600), color=color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"{label}.png")


def create_patients() -> list[Paciente]:
    first_names = [
        "María",
        "Carlos",
        "Lucía",
        "Jorge",
        "Rosa",
        "Pedro",
        "Ana",
        "Miguel",
        "Elena",
        "Sofía",
    ]
    second_names = [
        "Elena",
        "Alberto",
        "Fernanda",
        "Luis",
        "Patricia",
        "Javier",
        "Milagros",
        "René",
        "Carmen",
        "Valeria",
    ]
    last_names_1 = [
        "Quispe",
        "Vargas",
        "Soto",
        "Rojas",
        "Mendoza",
        "Castillo",
        "Torres",
        "Medina",
        "Paredes",
        "Salazar",
    ]
    last_names_2 = [
        "Lopez",
        "García",
        "Ramírez",
        "Huamán",
        "Tello",
        "Flores",
        "Ramos",
        "Cruz",
        "Luna",
        "Córdova",
    ]

    patients: list[Paciente] = []
    for index in range(10):
        patient = Paciente.objects.create(
            nombres=f"{first_names[index % len(first_names)]} {second_names[index % len(second_names)]}",
            apellidos=f"{last_names_1[index % len(last_names_1)]} {last_names_2[index % len(last_names_2)]}",
            dni=f"{70000000 + index:08d}",
            fecha_nacimiento=date(1960 + (index % 35), ((index % 12) + 1), min(((index * 3) % 28) + 1, 28)),
            sexo="F" if index % 2 == 0 else "M",
            telefono=f"9{index:08d}"[-9:],
        )
        patients.append(patient)

    return patients


def create_personal() -> tuple[list[Personal], list[Personal]]:
    medicos = [
        Personal.objects.create(nombre_completo="Dr. José Luis Mendoza", rol="medico", colegiatura="CMP 44122", activo=True),
        Personal.objects.create(nombre_completo="Dra. Ana Patricia Ríos", rol="medico", colegiatura="CMP 55881", activo=True),
        Personal.objects.create(nombre_completo="Dr. Marco Aurelio Campos", rol="medico", colegiatura="CMP 66773", activo=True),
        Personal.objects.create(nombre_completo="Dra. Valeria Paredes", rol="medico", colegiatura="CMP 77441", activo=True),
        Personal.objects.create(nombre_completo="Dr. Ernesto Salazar", rol="medico", colegiatura="CMP 88219", activo=True),
    ]
    enfermeras = [
        Personal.objects.create(nombre_completo="Enf. Rosa Castillo", rol="enfermera", colegiatura="ENF 23881", activo=True),
        Personal.objects.create(nombre_completo="Enf. Miguel Huamán", rol="enfermera", colegiatura="ENF 11442", activo=True),
    ]
    return medicos, enfermeras


def create_colonoscopia_case(
    *,
    paciente: Paciente,
    medico: Personal,
    enfermera: Personal,
    fecha: date,
    motivo: str,
    antecedentes: str,
    sedacion: str,
    farmacos: str,
    tiempo_retiro_min: float,
    intubacion_cecal: bool,
    foto_doc_ciego: bool,
    ileoscopia_distal: bool,
    boston: tuple[int, int, int],
    insp_pasiva: str,
    insp_activa: str,
    tacto_rectal: str,
    canal_anal: str,
    segmentos: dict[str, tuple[str, str]],
    biopsias: list[tuple[str, str, int | None]],
    diagnosticos: list[str],
    sugerencias: list[str],
    created_by,
) -> Colonoscopia:
    colonoscopia = Colonoscopia.objects.create(
        paciente=paciente,
        medico=medico,
        enfermera=enfermera,
        fecha=fecha,
        motivo=motivo,
        antecedentes=antecedentes,
        sedacion=sedacion,
        farmacos=farmacos,
        tiempo_retiro_min=tiempo_retiro_min,
        intubacion_cecal=intubacion_cecal,
        foto_doc_ciego=foto_doc_ciego,
        ileoscopia_distal=ileoscopia_distal,
        boston_cd=boston[0],
        boston_ct=boston[1],
        boston_ci=boston[2],
        insp_pasiva=insp_pasiva,
        insp_activa=insp_activa,
        tacto_rectal=tacto_rectal,
        canal_anal=canal_anal,
        creado_por=created_by,
    )

    for key, (estado, texto) in segmentos.items():
        SegmentoColon.objects.create(
            colonoscopia=colonoscopia,
            segmento=key,
            estado=estado,
            texto=texto,
        )

    for frasco, descripcion, n_lesiones in biopsias:
        BiopsiaColonoscopia.objects.create(
            colonoscopia=colonoscopia,
            frasco=frasco,
            descripcion=descripcion,
            n_lesiones=n_lesiones,
        )

    for index, texto in enumerate(diagnosticos):
        DiagnosticoColonoscopia.objects.create(colonoscopia=colonoscopia, texto=texto, orden=index)

    for index, texto in enumerate(sugerencias):
        SugerenciaColonoscopia.objects.create(colonoscopia=colonoscopia, texto=texto, orden=index)

    return colonoscopia


def create_eda_case(
    *,
    paciente: Paciente,
    medico: Personal,
    enfermera: Personal,
    fecha: date,
    motivo: str,
    antecedentes: str,
    sedacion: str,
    farmacos: str,
    tiempo_examen_min: int,
    peace: tuple[int, int, int],
    segmentos: dict[str, tuple[str, str, str, str]],
    biopsias: list[tuple[str, str, int | None]],
    diagnosticos: list[str],
    sugerencias: list[str],
    created_by,
) -> EDA:
    eda = EDA.objects.create(
        paciente=paciente,
        medico=medico,
        enfermera=enfermera,
        fecha=fecha,
        motivo=motivo,
        antecedentes=antecedentes,
        sedacion=sedacion,
        farmacos=farmacos,
        tiempo_examen_min=tiempo_examen_min,
        peace_esofago=peace[0],
        peace_estomago=peace[1],
        peace_duodeno=peace[2],
        creado_por=created_by,
    )

    for key, (estado, texto, hill, piloro) in segmentos.items():
        SegmentoEDA.objects.create(
            eda=eda,
            segmento=key,
            estado=estado,
            texto=texto,
            cardias_hill=hill,
            piloro=piloro,
        )

    for frasco, descripcion, n_lesiones in biopsias:
        BiopsiaEDA.objects.create(
            eda=eda,
            frasco=frasco,
            descripcion=descripcion,
            n_lesiones=n_lesiones,
        )

    for index, texto in enumerate(diagnosticos):
        DiagnosticoEDA.objects.create(eda=eda, texto=texto, orden=index)

    for index, texto in enumerate(sugerencias):
        SugerenciaEDA.objects.create(eda=eda, texto=texto, orden=index)

    return eda


def main() -> None:
    call_command("migrate", interactive=False, verbosity=0)

    ImagenEndoscopica.objects.all().delete()
    for model in [
        ProcedimientoGastro,
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

    for procedure_data in DEFAULT_PROCEDURE_CATALOG:
        ProcedimientoGastro.objects.create(**procedure_data)

    media_demo = Path(settings.MEDIA_ROOT) / "endoscopia"
    shutil.rmtree(media_demo, ignore_errors=True)
    media_demo.mkdir(parents=True, exist_ok=True)

    ensure_access_groups()
    lectura_group = Group.objects.get(name=READ_GROUP)
    escritura_group = Group.objects.get(name=WRITE_GROUP)
    total_group = Group.objects.get(name=ALL_GROUP)

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

    demo_read, _ = User.objects.get_or_create(
        username="demo_read",
        defaults={
            "first_name": "Demo",
            "last_name": "Lectura",
            "is_active": True,
        },
    )
    demo_read.set_password("demo1234")
    demo_read.is_active = True
    demo_read.is_staff = False
    demo_read.is_superuser = False
    demo_read.save()
    demo_read.groups.set([lectura_group])

    demo_write, _ = User.objects.get_or_create(
        username="demo_write",
        defaults={
            "first_name": "Demo",
            "last_name": "Escritura",
            "is_active": True,
        },
    )
    demo_write.set_password("demo1234")
    demo_write.is_active = True
    demo_write.is_staff = False
    demo_write.is_superuser = False
    demo_write.save()
    demo_write.groups.set([escritura_group])

    demo_admin, _ = User.objects.get_or_create(
        username="demo_admin",
        defaults={
            "first_name": "Demo",
            "last_name": "Total",
            "is_active": True,
        },
    )
    demo_admin.set_password("demo1234")
    demo_admin.is_active = True
    demo_admin.is_staff = False
    demo_admin.is_superuser = False
    demo_admin.save()
    demo_admin.groups.set([total_group])

    pacientes = create_patients()
    medicos, enfermeras = create_personal()

    colon_cases = [
        dict(
            paciente=pacientes[0],
            medico=medicos[0],
            enfermera=enfermeras[0],
            fecha=date(2026, 6, 18),
            motivo="Sangrado digestivo bajo intermitente y control de pólipos previos.",
            antecedentes="Antecedente familiar de cáncer colorrectal. Colonoscopía previa hace 4 años.",
            sedacion="consciente",
            farmacos="Midazolam + propofol titulado",
            tiempo_retiro_min=9.5,
            intubacion_cecal=True,
            foto_doc_ciego=True,
            ileoscopia_distal=False,
            boston=(2, 2, 1),
            insp_pasiva="Sin lesiones externas visibles.",
            insp_activa="Sin cambios significativos con pujo.",
            tacto_rectal="Canal anal sin masas palpables.",
            canal_anal="Normotónico.",
            segmentos={
                "ciego": ("normal", ""),
                "ascendente": ("normal", ""),
                "transverso": ("normal", ""),
                "descendente": ("alterado", "Mucosa con leve congestión focal y pequeña erosión superficial."),
                "sigmoides": ("alterado", "Diverticulosis múltiple sin estigmas de sangrado."),
                "recto": ("normal", ""),
            },
            biopsias=[
                ("A1", "Biopsia de mucosa en descendente", 1),
                ("A2", "Muestra de lesión en sigmoides", 2),
            ],
            diagnosticos=[
                "Diverticulosis colónica no complicada.",
                "Erosiones focales en colon descendente.",
            ],
            sugerencias=[
                "Control clínico y dieta rica en fibra.",
                "Retomar control endoscópico según anatomía patológica.",
            ],
        ),
        dict(
            paciente=pacientes[1],
            medico=medicos[1],
            enfermera=enfermeras[1],
            fecha=date(2026, 6, 21),
            motivo="Tamizaje por edad y antecedente de anemia ferropénica.",
            antecedentes="Sin procedimientos previos relevantes.",
            sedacion="profunda",
            farmacos="Propofol",
            tiempo_retiro_min=12,
            intubacion_cecal=True,
            foto_doc_ciego=True,
            ileoscopia_distal=True,
            boston=(3, 3, 3),
            insp_pasiva="Inspección anal sin hallazgos patológicos.",
            insp_activa="Sin prolapsos ni sangrado.",
            tacto_rectal="Sin dolor ni masas.",
            canal_anal="Adecuado.",
            segmentos={segmento: ("normal", "") for segmento in ["ciego", "ascendente", "transverso", "descendente", "sigmoides", "recto"]},
            biopsias=[("B1", "Biopsia de pólipo diminuto en recto", 1)],
            diagnosticos=["Examen sin lesiones significativas.", "Pólipo rectal diminuto resecado."] ,
            sugerencias=["Control preventivo según hallazgos histológicos.", "Repetir colonoscopía según resultado anatomopatológico."],
        ),
        dict(
            paciente=pacientes[2],
            medico=medicos[2],
            enfermera=enfermeras[0],
            fecha=date(2026, 6, 24),
            motivo="Dolor abdominal recurrente y cambio en ritmo deposicional.",
            antecedentes="Síndrome de intestino irritable en estudio.",
            sedacion="consciente",
            farmacos="Midazolam",
            tiempo_retiro_min=8.5,
            intubacion_cecal=True,
            foto_doc_ciego=False,
            ileoscopia_distal=False,
            boston=(2, 2, 2),
            insp_pasiva="Sin lesiones externas visibles.",
            insp_activa="Moderada sensibilidad al tacto.",
            tacto_rectal="Sin masas, dolor leve.",
            canal_anal="Normotónico.",
            segmentos={
                "ciego": ("normal", ""),
                "ascendente": ("alterado", "Mucosa con edema leve y patrón vascular disminuido."),
                "transverso": ("normal", ""),
                "descendente": ("alterado", "Mucosa friable con congestión parcheada."),
                "sigmoides": ("normal", ""),
                "recto": ("normal", ""),
            },
            biopsias=[("C1", "Biopsia de colon descendente", 1)],
            diagnosticos=["Colitis inespecífica leve.", "Mucosa friable en descendente."],
            sugerencias=["Correlación con clínica y coprológico.", "Control ambulatorio con gastroenterología."],
        ),
        dict(
            paciente=pacientes[3],
            medico=medicos[3],
            enfermera=enfermeras[1],
            fecha=date(2026, 6, 27),
            motivo="Seguimiento por pólipo resecado previamente.",
            antecedentes="Polipectomía hace 12 meses.",
            sedacion="profunda",
            farmacos="Propofol",
            tiempo_retiro_min=10.2,
            intubacion_cecal=True,
            foto_doc_ciego=True,
            ileoscopia_distal=True,
            boston=(3, 2, 2),
            insp_pasiva="Sin sangrado activo.",
            insp_activa="Sin hallazgos significativos.",
            tacto_rectal="Sin masas palpables.",
            canal_anal="Adecuado.",
            segmentos={
                "ciego": ("normal", ""),
                "ascendente": ("normal", ""),
                "transverso": ("normal", ""),
                "descendente": ("normal", ""),
                "sigmoides": ("alterado", "Pequeño pólipo sésil de 4 mm."),
                "recto": ("normal", ""),
            },
            biopsias=[("D1", "Pólipo sigmoideo resecado", 1)],
            diagnosticos=["Pólipo sésil de sigmoides.", "Restos de polipectomía previa sin complicaciones."],
            sugerencias=["Control endoscópico en 12 meses.", "Esperar anatomía patológica."],
        ),
        dict(
            paciente=pacientes[4],
            medico=medicos[4],
            enfermera=enfermeras[0],
            fecha=date(2026, 6, 30),
            motivo="Dolor rectal y rectorragia escasa.",
            antecedentes="Hemorroides conocidas.",
            sedacion="ninguna",
            farmacos="Ninguno",
            tiempo_retiro_min=7.8,
            intubacion_cecal=True,
            foto_doc_ciego=False,
            ileoscopia_distal=False,
            boston=(2, 3, 2),
            insp_pasiva="Pequeñas hemorroides internas visibles.",
            insp_activa="Sangrado mínimo al roce.",
            tacto_rectal="Canal anal sin masas, dolor leve.",
            canal_anal="Hemorroidal.",
            segmentos={segmento: ("normal", "") for segmento in ["ciego", "ascendente", "transverso", "descendente", "sigmoides", "recto"]},
            biopsias=[("E1", "Muestra de mucosa rectal", 1)],
            diagnosticos=["Hemorroides internas grado I.", "Recto sin otras lesiones macroscópicas."],
            sugerencias=["Tratamiento conservador.", "Control si persiste la rectorragia."],
        ),
    ]

    eda_cases = [
        dict(
            paciente=pacientes[5],
            medico=medicos[0],
            enfermera=enfermeras[1],
            fecha=date(2026, 6, 20),
            motivo="Dispepsia y pirosis de varios meses de evolución.",
            antecedentes="Uso ocasional de AINEs.",
            sedacion="consciente",
            farmacos="Midazolam",
            tiempo_examen_min=7,
            peace=(2, 3, 2),
            segmentos={
                "esofago": ("normal", "", "", ""),
                "fondo": ("alterado", "Plegues gástricos discretamente engrosados.", "hill2", ""),
                "cuerpo": ("normal", "", "", ""),
                "angulo": ("normal", "", "", ""),
                "antro": ("alterado", "Eritema antral leve, sin erosiones.", "", "centrico"),
                "bulbo": ("normal", "", "", ""),
                "segporcion": ("normal", "", "", ""),
            },
            biopsias=[("C1", "Biopsia antral por gastritis", 1), ("C2", "Biopsia de esófago distal", 1)],
            diagnosticos=["Gastritis antral leve.", "Reflujo gastroesofágico no erosivo."],
            sugerencias=["Higiene dietética y control con gastroenterología.", "Esperar anatomía patológica si corresponde."],
        ),
        dict(
            paciente=pacientes[6],
            medico=medicos[1],
            enfermera=enfermeras[0],
            fecha=date(2026, 6, 22),
            motivo="Dolor epigástrico y náuseas postprandiales.",
            antecedentes="Sin cirugía previa.",
            sedacion="naap",
            farmacos="Propofol",
            tiempo_examen_min=6,
            peace=(3, 3, 3),
            segmentos={segmento: ("normal", "", "", "") for segmento in ["esofago", "fondo", "cuerpo", "angulo", "antro", "bulbo", "segporcion"]},
            biopsias=[("D1", "Sin biopsias", None)],
            diagnosticos=["Endoscopía alta sin alteraciones macroscópicas."],
            sugerencias=["Seguimiento clínico."],
        ),
        dict(
            paciente=pacientes[7],
            medico=medicos[2],
            enfermera=enfermeras[1],
            fecha=date(2026, 6, 23),
            motivo="Pérdida de peso y plenitud precoz.",
            antecedentes="Sin antecedentes quirúrgicos.",
            sedacion="profunda",
            farmacos="Propofol",
            tiempo_examen_min=8,
            peace=(2, 2, 2),
            segmentos={
                "esofago": ("normal", "", "", ""),
                "fondo": ("alterado", "Herida mucosa superficial sin sangrado.", "hill1", ""),
                "cuerpo": ("alterado", "Eritema difuso leve.", "", ""),
                "angulo": ("normal", "", "", ""),
                "antro": ("alterado", "Mucosa eritematosa y friable.", "", "deformado"),
                "bulbo": ("normal", "", "", ""),
                "segporcion": ("normal", "", "", ""),
            },
            biopsias=[("E1", "Biopsia antral y corporal", 2)],
            diagnosticos=["Gastropatía eritematosa difusa.", "Sospecha de infección por H. pylori."],
            sugerencias=["Iniciar manejo según anatomía patológica.", "Control con gastroenterología."],
        ),
        dict(
            paciente=pacientes[8],
            medico=medicos[3],
            enfermera=enfermeras[0],
            fecha=date(2026, 6, 26),
            motivo="Pirosis y regurgitación nocturna.",
            antecedentes="Tratamiento intermitente con IBP.",
            sedacion="consciente",
            farmacos="Midazolam",
            tiempo_examen_min=7,
            peace=(3, 2, 2),
            segmentos={
                "esofago": ("alterado", "Eritema distal y línea Z irregular.", "", ""),
                "fondo": ("normal", "", "hill3", ""),
                "cuerpo": ("normal", "", "", ""),
                "angulo": ("normal", "", "", ""),
                "antro": ("normal", "", "", "centrico"),
                "bulbo": ("normal", "", "", ""),
                "segporcion": ("normal", "", "", ""),
            },
            biopsias=[("F1", "Biopsia de línea Z", 1)],
            diagnosticos=["Reflujo gastroesofágico con esofagitis leve.", "Hernia hiatal pequeña."],
            sugerencias=["Optimizar IBP.", "Elevar cabecera y medidas antirreflujo."],
        ),
        dict(
            paciente=pacientes[9],
            medico=medicos[4],
            enfermera=enfermeras[1],
            fecha=date(2026, 6, 29),
            motivo="Anemia y melena referidas en consulta externa.",
            antecedentes="Uso reciente de AINEs.",
            sedacion="profunda",
            farmacos="Propofol",
            tiempo_examen_min=9,
            peace=(2, 2, 3),
            segmentos={
                "esofago": ("normal", "", "", ""),
                "fondo": ("normal", "", "hill2", ""),
                "cuerpo": ("alterado", "Eritema focal con pequeñas erosiones.", "", ""),
                "angulo": ("normal", "", "", ""),
                "antro": ("alterado", "Eritema antral con erosiones lineales.", "", "estenotico"),
                "bulbo": ("alterado", "Bulbo con edema y eritema.", "", ""),
                "segporcion": ("normal", "", "", ""),
            },
            biopsias=[("G1", "Biopsia de antro y bulbo", 2)],
            diagnosticos=["Duodenitis erosiva leve.", "Gastropatía por AINEs probable."],
            sugerencias=["Suspender AINEs si es posible.", "Control y tratamiento antisecretor."],
        ),
    ]

    colon_cases.extend([
        dict(
            paciente=pacientes[0],
            medico=medicos[1],
            enfermera=enfermeras[0],
            fecha=date(2026, 7, 1),
            motivo="Control de diverticulosis y sangrado previo.",
            antecedentes="Episodios esporádicos de rectorragia leve.",
            sedacion="consciente",
            farmacos="Midazolam titulado",
            tiempo_retiro_min=10.1,
            intubacion_cecal=True,
            foto_doc_ciego=True,
            ileoscopia_distal=False,
            boston=(2, 2, 2),
            insp_pasiva="Sin lesiones externas visibles.",
            insp_activa="Sin cambios relevantes con pujo.",
            tacto_rectal="Sin masas palpables.",
            canal_anal="Normotónico.",
            segmentos={
                "ciego": ("normal", ""),
                "ascendente": ("normal", ""),
                "transverso": ("normal", ""),
                "descendente": ("alterado", "Congestión leve persistente en descendente."),
                "sigmoides": ("alterado", "Divertículos múltiples sin sangrado activo."),
                "recto": ("normal", ""),
            },
            biopsias=[("A3", "Biopsia de mucosa descendente", 1)],
            diagnosticos=["Diverticulosis estable.", "Cambios inflamatorios leves en colon descendente."],
            sugerencias=["Mantener dieta rica en fibra.", "Control según evolución clínica."],
        ),
        dict(
            paciente=pacientes[1],
            medico=medicos[2],
            enfermera=enfermeras[1],
            fecha=date(2026, 7, 2),
            motivo="Revisión por anemia ferropénica y pólipo previo.",
            antecedentes="Sin complicaciones en procedimientos previos.",
            sedacion="profunda",
            farmacos="Propofol",
            tiempo_retiro_min=11.4,
            intubacion_cecal=True,
            foto_doc_ciego=True,
            ileoscopia_distal=True,
            boston=(3, 3, 3),
            insp_pasiva="Inspección anal sin alteraciones.",
            insp_activa="Sin sangrado ni prolapsos.",
            tacto_rectal="Sin dolor.",
            canal_anal="Adecuado.",
            segmentos={segmento: ("normal", "") for segmento in ["ciego", "ascendente", "transverso", "descendente", "sigmoides", "recto"]},
            biopsias=[("B2", "Biopsia de mucosa rectal", 1)],
            diagnosticos=["Control endoscópico sin lesiones relevantes."],
            sugerencias=["Continuar seguimiento por medicina interna."],
        ),
    ])

    eda_cases.extend([
        dict(
            paciente=pacientes[0],
            medico=medicos[1],
            enfermera=enfermeras[0],
            fecha=date(2026, 7, 3),
            motivo="Control por reflujo y hallazgos de gastritis previa.",
            antecedentes="Mejoría parcial con IBP.",
            sedacion="consciente",
            farmacos="Midazolam",
            tiempo_examen_min=7,
            peace=(2, 2, 2),
            segmentos={
                "esofago": ("normal", "", "", ""),
                "fondo": ("alterado", "Plegues discretamente engrosados.", "hill2", ""),
                "cuerpo": ("normal", "", "", ""),
                "angulo": ("normal", "", "", ""),
                "antro": ("alterado", "Eritema leve en antro.", "", "centrico"),
                "bulbo": ("normal", "", "", ""),
                "segporcion": ("normal", "", "", ""),
            },
            biopsias=[("C3", "Biopsia antral de control", 1)],
            diagnosticos=["Gastritis leve persistente."],
            sugerencias=["Continuar IBP y medidas dietéticas."],
        ),
        dict(
            paciente=pacientes[2],
            medico=medicos[3],
            enfermera=enfermeras[1],
            fecha=date(2026, 7, 4),
            motivo="Seguimiento de dispepsia y síntomas de reflujo.",
            antecedentes="Tratamiento irregular con IBP.",
            sedacion="profunda",
            farmacos="Propofol",
            tiempo_examen_min=6,
            peace=(3, 2, 2),
            segmentos={
                "esofago": ("alterado", "Eritema distal leve.", "", ""),
                "fondo": ("normal", "", "hill1", ""),
                "cuerpo": ("normal", "", "", ""),
                "angulo": ("normal", "", "", ""),
                "antro": ("alterado", "Eritema antral leve sin erosiones.", "", "centrico"),
                "bulbo": ("normal", "", "", ""),
                "segporcion": ("normal", "", "", ""),
            },
            biopsias=[("D2", "Biopsia de línea Z y antro", 2)],
            diagnosticos=["Reflujo gastroesofágico leve.", "Gastritis antral leve."],
            sugerencias=["Optimizar tratamiento antisecretor.", "Reforzar medidas antirreflujo."],
        ),
        dict(
            paciente=pacientes[5],
            medico=medicos[4],
            enfermera=enfermeras[0],
            fecha=date(2026, 7, 5),
            motivo="Pirosis y dolor epigástrico persistente.",
            antecedentes="Sin cirugías previas.",
            sedacion="consciente",
            farmacos="Midazolam",
            tiempo_examen_min=7,
            peace=(2, 2, 2),
            segmentos={
                "esofago": ("normal", "", "", ""),
                "fondo": ("alterado", "Pequeña hernia hiatal.", "hill2", ""),
                "cuerpo": ("normal", "", "", ""),
                "angulo": ("normal", "", "", ""),
                "antro": ("alterado", "Gastritis leve antral.", "", "centrico"),
                "bulbo": ("normal", "", "", ""),
                "segporcion": ("normal", "", "", ""),
            },
            biopsias=[("E2", "Biopsia de antro", 1)],
            diagnosticos=["Hernia hiatal pequeña.", "Gastritis antral leve."],
            sugerencias=["Seguimiento ambulatorio.", "Control si persisten síntomas."],
        ),
    ])

    colonoscopias = [create_colonoscopia_case(created_by=demo_user, **case) for case in colon_cases]
    edas = [create_eda_case(created_by=demo_user, **case) for case in eda_cases]

    ct_colon = ContentType.objects.get_for_model(Colonoscopia)
    ct_eda = ContentType.objects.get_for_model(EDA)

    sample_images = [
        (ct_colon, colonoscopias[0], "colon-1", "Colonoscopía descendente", (22, 104, 128), 0),
        (ct_colon, colonoscopias[1], "colon-2", "Colonoscopía normal", (58, 142, 114), 1),
        (ct_colon, colonoscopias[2], "colon-3", "Colitis inespecífica", (154, 86, 72), 0),
        (ct_colon, colonoscopias[3], "colon-4", "Pólipo sigmoideo", (122, 96, 164), 0),
        (ct_colon, colonoscopias[4], "colon-5", "Hemorroides internas", (92, 126, 92), 0),
        (ct_eda, edas[0], "eda-1", "EDA fondo/antro", (162, 114, 59), 0),
        (ct_eda, edas[1], "eda-2", "EDA normal", (86, 95, 145), 1),
        (ct_eda, edas[2], "eda-3", "Gastropatía eritematosa", (126, 80, 57), 0),
        (ct_eda, edas[3], "eda-4", "Reflujo gastroesofágico", (74, 132, 159), 0),
        (ct_eda, edas[4], "eda-5", "Duodenitis erosiva", (147, 107, 78), 0),
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
    print("Usuarios demo: demo / demo1234, demo_read / demo1234, demo_write / demo1234, demo_admin / demo1234")
    print(f"Pacientes: {Paciente.objects.count()}")
    print(f"Personal: {Personal.objects.count()}")
    print(f"Colonoscopías: {Colonoscopia.objects.count()}")
    print(f"EDA: {EDA.objects.count()}")
    print(f"Imágenes: {ImagenEndoscopica.objects.count()}")


if __name__ == "__main__":
    main()