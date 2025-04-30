# from django.shortcuts import render
# from django.http import HttpResponse
# import requests

# # Create your views here. - You make the logic here and the template will be rendered in the template folder.

# def index(request):
#     return HttpResponse("Hello, world. You're at the CORE index.")

from django.shortcuts import render
from django.core.management import call_command
from django.contrib import messages
from CORE.celery import get_all_data_task

def obtener_indicadores(request):
    if request.method == 'POST':
        indicador = request.POST.get('indicador')
        try:
            if indicador == 'uf':
                call_command('get_uf_data')
                messages.success(request, '¡Datos de la UF obtenidos y guardados exitosamente!')
            elif indicador == 'euro':
                call_command('get_euro_data')
                messages.success(request, '¡Datos del Euro obtenidos y guardados exitosamente!')
            elif indicador == 'dolar':
                call_command('get_dolar_data')
                messages.success(request, '¡Datos del Dólar obtenidos y guardados exitosamente!')
            elif indicador == 'todo':
                get_all_data_task.delay() 
                messages.success(request, '¡Todos los datos han sido descargados!')
        except Exception as e:
            messages.error(request, f'Ocurrió un error: {e}')

    return render(request, 'core/obtener_indicadores.html')