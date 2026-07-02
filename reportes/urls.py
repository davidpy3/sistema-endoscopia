from django.urls import path

from . import views

app_name = "reportes"

urlpatterns = [
    path("colonoscopia/<int:pk>/pdf/", views.colonoscopia_pdf, name="colonoscopia_pdf"),
    path("eda/<int:pk>/pdf/", views.eda_pdf, name="eda_pdf"),
]