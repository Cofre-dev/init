from django.urls import path
from . import views

urlpatterns = [
    path('', views.obtener_indicadores, name='obtener_indicadores'),
    # path('descargar/<str:nombre_archivo>/', views.descargar_indicador, name='descargar_indicador'),
]