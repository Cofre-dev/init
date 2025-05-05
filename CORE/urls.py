from django.urls import path
from . import views

urlpatterns = [
    path('', views.obtener_indicadores, name='main_page'),
    path('descargar-dolar/', views.descargar_excel_dolar, name='descargar_excel_dolar'),
]