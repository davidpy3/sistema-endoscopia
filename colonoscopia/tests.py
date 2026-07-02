from datetime import date

from django.test import TestCase

from pacientes.models import Paciente
from personal.models import Personal

from .models import Colonoscopia, SegmentoColon, TEXTO_NORMAL_COLON
from .serializers import ColonoscopiaSerializer


class ColonoscopiaSegmentoRulesTests(TestCase):
	def setUp(self):
		self.paciente = Paciente.objects.create(
			nombres="Ana",
			apellidos="Lopez",
			dni="12345678",
			fecha_nacimiento=date(1990, 1, 1),
		)
		self.medico = Personal.objects.create(
			nombre_completo="Dr. Perez",
			rol="medico",
		)
		self.enfermera = Personal.objects.create(
			nombre_completo="Enf. Ruiz",
			rol="enfermera",
		)
		self.procedimiento = Colonoscopia.objects.create(
			paciente=self.paciente,
			medico=self.medico,
			enfermera=self.enfermera,
			fecha=date(2026, 7, 1),
		)
		SegmentoColon.objects.create(
			colonoscopia=self.procedimiento,
			segmento="ciego",
			estado="alterado",
			texto="Hallazgo alterado",
		)

	def test_segmento_normal_restores_standard_phrase(self):
		serializer = ColonoscopiaSerializer(
			instance=self.procedimiento,
			data={
				"segmentos": [
					{
						"segmento": "ciego",
						"estado": "normal",
						"texto": "",
					}
				]
			},
			partial=True,
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		serializer.save()

		segmento = SegmentoColon.objects.get(
			colonoscopia=self.procedimiento,
			segmento="ciego",
		)
		self.assertEqual(segmento.estado, "normal")
		self.assertEqual(segmento.texto, TEXTO_NORMAL_COLON["ciego"])
