from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, parsers

from .models import ImagenEndoscopica
from .serializers import ImagenEndoscopicaSerializer


class ImagenEndoscopicaViewSet(viewsets.ModelViewSet):
    queryset = ImagenEndoscopica.objects.all()
    serializer_class = ImagenEndoscopicaSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        tipo = self.request.query_params.get("tipo")
        object_id = self.request.query_params.get("object_id")
        if tipo:
            qs = qs.filter(content_type=ContentType.objects.get(app_label=tipo, model=tipo))
        if object_id:
            qs = qs.filter(object_id=object_id)
        return qs