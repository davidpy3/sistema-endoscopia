from datetime import date

from django.test import TestCase

from pacientes.models import Paciente
from personal.models import Personal

from .models import EDA, SegmentoEDA, TEXTO_NORMAL_EDA
from .serializers import EDASerializer


class EDASegmentoRulesTests(TestCase):
	def setUp(self):
		self.paciente = Paciente.objects.create(
			nombres="Carlos",
			apellidos="Torres",
			dni="87654321",
			fecha_nacimiento=date(1985, 5, 10),
		)
		self.medico = Personal.objects.create(
			nombre_completo="Dra. Salas",
			rol="medico",
		)
		self.enfermera = Personal.objects.create(
			nombre_completo="Enf. Ramos",
			rol="enfermera",
		)
		self.procedimiento = EDA.objects.create(
			paciente=self.paciente,
			medico=self.medico,
			enfermera=self.enfermera,
			fecha=date(2026, 7, 1),
		)
		SegmentoEDA.objects.create(
			eda=self.procedimiento,
			segmento="esofago",
			estado="alterado",
			texto="Hallazgo alterado",
		)

	def test_segmento_normal_restores_standard_phrase(self):
		serializer = EDASerializer(
			instance=self.procedimiento,
			data={
				"segmentos": [
					{
						"segmento": "esofago",
						"estado": "normal",
						"texto": "",
					}
				]
			},
			partial=True,
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		serializer.save()

		segmento = SegmentoEDA.objects.get(
			eda=self.procedimiento,
			segmento="esofago",
		)
		self.assertEqual(segmento.estado, "normal")
		self.assertEqual(segmento.texto, TEXTO_NORMAL_EDA["esofago"])
