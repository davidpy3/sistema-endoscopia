from datetime import date

from django.template.loader import render_to_string
from django.test import TestCase

from colonoscopia.models import Colonoscopia, SegmentoColon
from eda.models import EDA, SegmentoEDA
from pacientes.models import Paciente
from personal.models import Personal

from .utils import calcular_edad, yn


class ReportesTemplateTests(TestCase):
	def setUp(self):
		self.paciente = Paciente.objects.create(
			nombres="Lucia",
			apellidos="Vega",
			dni="11223344",
			fecha_nacimiento=date(1992, 4, 20),
		)
		self.medico = Personal.objects.create(
			nombre_completo="Dr. Gomez",
			rol="medico",
		)
		self.enfermera = Personal.objects.create(
			nombre_completo="Enf. Diaz",
			rol="enfermera",
		)

	def test_colonoscopia_template_rendering(self):
		colonoscopia = Colonoscopia.objects.create(
			paciente=self.paciente,
			medico=self.medico,
			enfermera=self.enfermera,
			fecha=date(2026, 7, 1),
			motivo="Control",
		)
		SegmentoColon.objects.create(
			colonoscopia=colonoscopia,
			segmento="ciego",
			estado="normal",
		)

		html = render_to_string(
			"reportes/colonoscopia_pdf.html",
			{
				"c": colonoscopia,
				"segmentos": colonoscopia.segmentos.all(),
				"biopsias": colonoscopia.biopsias.all(),
				"diagnosticos": colonoscopia.diagnosticos.all(),
				"sugerencias": colonoscopia.sugerencias.all(),
				"imagenes": [],
				"edad": calcular_edad(self.paciente.fecha_nacimiento, colonoscopia.fecha),
				"cecal_txt": yn(colonoscopia.intubacion_cecal),
				"ileo_txt": yn(colonoscopia.ileoscopia_distal),
				"boston_total": colonoscopia.boston_total,
				"prep_adecuada_txt": yn(colonoscopia.preparacion_adecuada),
			},
		)

		self.assertIn("HOSPITAL REGIONAL DE TUMBES", html)
		self.assertIn("Sin biopsias.", html)

	def test_eda_template_rendering(self):
		eda = EDA.objects.create(
			paciente=self.paciente,
			medico=self.medico,
			enfermera=self.enfermera,
			fecha=date(2026, 7, 1),
			motivo="Dispepsia",
		)
		SegmentoEDA.objects.create(
			eda=eda,
			segmento="fondo",
			estado="normal",
			cardias_hill="hill2",
		)

		html = render_to_string(
			"reportes/eda_pdf.html",
			{
				"e": eda,
				"segmentos": eda.segmentos.all(),
				"biopsias": eda.biopsias.all(),
				"diagnosticos": eda.diagnosticos.all(),
				"sugerencias": eda.sugerencias.all(),
				"imagenes": [],
				"edad": calcular_edad(self.paciente.fecha_nacimiento, eda.fecha),
				"peace_total": eda.peace_total,
			},
		)

		self.assertIn("ENDOSCOPÍA DIGESTIVA ALTA", html)
		self.assertIn("Hill II", html)
