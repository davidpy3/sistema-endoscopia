from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .models import EDA
from .serializers import EDASerializer


class EDAViewSet(viewsets.ModelViewSet):
    queryset = EDA.objects.select_related(
        "paciente", "medico", "enfermera"
    ).prefetch_related("segmentos", "biopsias", "diagnosticos", "sugerencias")
    serializer_class = EDASerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["medico", "fecha"]
    search_fields = ["paciente__nombres", "paciente__apellidos", "paciente__dni"]
    ordering_fields = ["fecha", "creado_en"]