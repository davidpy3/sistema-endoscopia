from django.urls import path

from .views import ProcedureCatalogView

app_name = 'procedimientos'

urlpatterns = [
	path('catalogo/', ProcedureCatalogView.as_view(), name='catalogo'),
]
