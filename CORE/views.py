from django.shortcuts import render
from django.core.management import call_command
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
import io
from openpyxl import load_workbook  # Si ya estás usando openpyxl

def obtener_indicadores(request):
    if request.method == 'POST':
        indicador = request.POST.get('indicador')
        try:
            output = io.BytesIO()
            nombre_archivo = None

            if indicador == 'uf':
                call_command('get_uf_data', output=output)
                nombre_archivo = f"UF_{datetime.now().strftime('%Y%m%d')}.xlsx"
            elif indicador == 'euro':
                call_command('get_euro_data', output=output)
                nombre_archivo = f"EURO_{datetime.now().strftime('%Y%m%d')}.xlsx"
            elif indicador == 'dolar':
                call_command('get_dolar_data', output=output)
                nombre_archivo = f"DOLAR_{datetime.now().strftime('%Y%m%d')}.xlsx"

            if nombre_archivo:
                response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
                messages.success(request, f'¡Datos de {indicador.upper()} obtenidos y listos para descargar!')
                return response
            else:
                messages.error(request, 'Ocurrió un error al generar los datos.')

        except Exception as e:
            messages.error(request, f'Ocurrió un error: {e}')

    return render(request, 'core/obtener_indicadores.html')