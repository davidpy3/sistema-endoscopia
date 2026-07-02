from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML

from colonoscopia.models import Colonoscopia, SEGMENTOS_COLON
from eda.models import EDA, SEGMENTOS_EDA
from imagenes.models import ImagenEndoscopica
from users.services import can_read

from .utils import calcular_edad, yn


def _imagenes_para(modelo, pk):
    ct = ContentType.objects.get_for_model(modelo)
    qs = ImagenEndoscopica.objects.filter(content_type=ct, object_id=pk).order_by("orden")
    # WeasyPrint resuelve más confiable con file:// que pidiéndose la imagen a sí mismo por HTTP
    return [
        {"url": f"file://{im.archivo.path}", "epigrafe": im.epigrafe}
        for im in qs
        if im.archivo
    ]


def _pdf_response(html_string, filename, request):
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    disposition = "inline" if request.GET.get("inline") else "attachment"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response


def colonoscopia_pdf(request, pk):
    if not can_read(request.user):
        return HttpResponseForbidden("Authentication required")

    c = get_object_or_404(
        Colonoscopia.objects.select_related("paciente", "medico", "enfermera").prefetch_related(
            "segmentos", "biopsias", "diagnosticos", "sugerencias"
        ),
        pk=pk,
    )

    orden = [key for key, _ in SEGMENTOS_COLON]
    segmentos = sorted(c.segmentos.all(), key=lambda s: orden.index(s.segmento))

    context = {
        "c": c,
        "segmentos": segmentos,
        "biopsias": c.biopsias.all(),
        "diagnosticos": c.diagnosticos.all(),
        "sugerencias": c.sugerencias.all(),
        "imagenes": _imagenes_para(Colonoscopia, c.pk),
        "edad": calcular_edad(c.paciente.fecha_nacimiento, c.fecha),
        "cecal_txt": yn(c.intubacion_cecal),
        "ileo_txt": yn(c.ileoscopia_distal),
        "boston_total": c.boston_total,
        "prep_adecuada_txt": yn(c.preparacion_adecuada),
    }

    html_string = render_to_string("reportes/colonoscopia_pdf.html", context)
    filename = f"colonoscopia_{c.paciente.dni}_{c.fecha}.pdf"
    return _pdf_response(html_string, filename, request)


def eda_pdf(request, pk):
    if not can_read(request.user):
        return HttpResponseForbidden("Authentication required")

    e = get_object_or_404(
        EDA.objects.select_related("paciente", "medico", "enfermera").prefetch_related(
            "segmentos", "biopsias", "diagnosticos", "sugerencias"
        ),
        pk=pk,
    )

    orden = [key for key, _ in SEGMENTOS_EDA]
    segmentos = sorted(e.segmentos.all(), key=lambda s: orden.index(s.segmento))

    context = {
        "e": e,
        "segmentos": segmentos,
        "biopsias": e.biopsias.all(),
        "diagnosticos": e.diagnosticos.all(),
        "sugerencias": e.sugerencias.all(),
        "imagenes": _imagenes_para(EDA, e.pk),
        "edad": calcular_edad(e.paciente.fecha_nacimiento, e.fecha),
        "peace_total": e.peace_total,
    }

    html_string = render_to_string("reportes/eda_pdf.html", context)
    filename = f"eda_{e.paciente.dni}_{e.fecha}.pdf"
    return _pdf_response(html_string, filename, request)