from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .models import Colonoscopia
from .serializers import ColonoscopiaSerializer


class ColonoscopiaViewSet(viewsets.ModelViewSet):
    queryset = Colonoscopia.objects.select_related(
        "paciente", "medico", "enfermera"
    ).prefetch_related("segmentos", "biopsias", "diagnosticos", "sugerencias")
    serializer_class = ColonoscopiaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["medico", "fecha", "intubacion_cecal", "ileoscopia_distal"]
    search_fields = ["paciente__nombres", "paciente__apellidos", "paciente__dni"]
    ordering_fields = ["fecha", "creado_en"]