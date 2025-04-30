from django.urls import path
from . import views

urlpatterns = [
    path('', views.obtener_indicadores, name='main_page'),  # La ruta vacía ahora apunta a tu vista
]