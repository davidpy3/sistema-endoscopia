from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action

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

    @action(detail=True, methods=["get"], url_path="draft")
    def draft(self, request, *args, **kwargs):
        instance = self.get_object()
        response = JsonResponse(self.get_serializer(instance).data)
        response["Content-Disposition"] = (
            f'attachment; filename="colonoscopia_{instance.pk}_draft.json"'
        )
        return response

    @action(detail=False, methods=["post"], url_path="from-draft")
    def from_draft(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return JsonResponse(self.get_serializer(instance).data, status=201)