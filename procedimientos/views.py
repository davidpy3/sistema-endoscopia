from authentication.permissions import RoleBasedAccessPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProcedimientoGastro


class ProcedureCatalogView(APIView):
	permission_classes = [RoleBasedAccessPermission]

	def get(self, request, *args, **kwargs):
		procedures = ProcedimientoGastro.objects.filter(activo=True).order_by("orden", "id")
		return Response([
			{
				"id": procedure.id,
				"code": procedure.codigo,
				"name": procedure.nombre,
				"description": procedure.descripcion,
				"scope": procedure.alcance,
			}
			for procedure in procedures
		])
