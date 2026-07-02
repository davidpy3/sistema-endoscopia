from rest_framework import viewsets, filters

from authentication.permissions import SuperuserWritePermission

from .models import Paciente
from .serializers import PacienteSerializer


class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [SuperuserWritePermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombres", "apellidos", "dni"]