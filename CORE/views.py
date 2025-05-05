from django.shortcuts import render, redirect
from django.core.management import call_command
from django.contrib import messages
from django.http import FileResponse
import os
from datetime import datetime

def obtener_indicadores(request):
    nombre_archivo_descarga = None
    if request.method == 'POST':
        indicador = request.POST.get('indicador')
        try:
            if indicador == 'uf':
                call_command('get_uf_data')
                nombre_archivo = f"UF_{datetime.now().strftime('%Y%m%d')}.xlsx"
                ruta_descargas_servidor = '/opt/render/Downloads/IndicadoresBCCH/'
                ruta_completa = os.path.join(ruta_descargas_servidor, nombre_archivo)
                messages.success(request, '¡Datos de la UF obtenidos y guardados exitosamente!')
                nombre_archivo_descarga = nombre_archivo
                
            elif indicador == 'euro':
                call_command('get_euro_data')
                nombre_archivo = f"EURO_{datetime.now().strftime('%Y%m%d')}.xlsx"
                ruta_descargas_servidor = '/opt/render/Downloads/IndicadoresBCCH/'
                ruta_completa = os.path.join(ruta_descargas_servidor, nombre_archivo)
                messages.success(request, '¡Datos del EURO obtenidos y guardados exitosamente!')
                nombre_archivo_descarga = nombre_archivo
                
            elif indicador == 'dolar':
                call_command('get_dolar_data')
                nombre_archivo = f"DOLAR_{datetime.now().strftime('%Y%m%d')}.xlsx"
                ruta_descargas_servidor = '/opt/render/Downloads/IndicadoresBCCH/'
                ruta_completa = os.path.join(ruta_descargas_servidor, nombre_archivo)
                messages.success(request, '¡Datos del Dólar obtenidos y guardados exitosamente!')
                nombre_archivo_descarga = nombre_archivo

        except Exception as e:
            messages.error(request, f'Ocurrió un error: {e}')

    return render(request, 'core/obtener_indicadores.html', {'nombre_archivo_descarga': nombre_archivo_descarga})