from rest_framework import viewsets, filters

from authentication.permissions import SuperuserWritePermission

from .models import Personal
from .serializers import PersonalSerializer


class PersonalViewSet(viewsets.ModelViewSet):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer
    permission_classes = [SuperuserWritePermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre_completo", "colegiatura"]

    def get_queryset(self):
        qs = super().get_queryset()
        rol = self.request.query_params.get("rol")
        if rol:
            qs = qs.filter(rol=rol)
        return qs