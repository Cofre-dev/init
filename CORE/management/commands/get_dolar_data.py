from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
import pandas as pd
import os
from datetime import datetime
import requests

# Configuración
USD_CODE = "F073.TCO.PRE.Z.D"
API_USER = "rojascofrem@gmail.com"
API_PASS = "Mat.FVC965"

def obtener_datos_bcch(indicador, fecha_inicio, fecha_fin):
    """
    Obtiene datos del Banco Central de Chile desde su API.
    """
    try:
        url = (
            f"https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx?"
            f"user={API_USER}&pass={API_PASS}&"
            f"firstdate={fecha_inicio}&lastdate={fecha_fin}&"
            f"timeseries={indicador}&function=GetSeries"
        )

        respuesta = requests.get(url, timeout=30)
        respuesta.raise_for_status()
        return respuesta.json()
    except Exception as e:
        print(f"Error al obtener datos de la API: {str(e)}")
        return None

def descargar_excel_dolar(request):
    """
    Vista que genera un archivo Excel con los datos del dólar
    y lo envía como descarga al navegador.
    """
    fecha_inicio = (datetime.now() - pd.DateOffset(months=1)).strftime("%Y-%m-%d")
    fecha_fin = datetime.now().strftime("%Y-%m-%d")

    datos = obtener_datos_bcch(USD_CODE, fecha_inicio, fecha_fin)
    if not datos:
        messages.error(request, 'No se recibieron datos válidos de la API.')
        return render(request, 'core/obtener_indicadores.html')

    if 'Series' not in datos or 'Obs' not in datos['Series']:
        messages.error(request, 'Estructura de datos inesperada.')
        return render(request, 'core/obtener_indicadores.html')

    # Procesar los datos en un DataFrame de pandas
    df = pd.DataFrame(datos['Series']['Obs'])
    df = df.drop(columns=['statusCode'], errors='ignore')  # Eliminar la columna statusCode si existe
    df = df.rename(columns={
        'indexDateString': 'Fecha',
        'value': 'Valor'
    })
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

    # Crear el archivo Excel en memoria
    nombre_archivo = f"DOLAR_{datetime.now().strftime('%Y%m%d')}.xlsx"
    with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dólar')

    # Leer el archivo Excel desde disco y enviarlo como respuesta HTTP
    with open(nombre_archivo, 'rb') as archivo_excel:
        response = HttpResponse(archivo_excel.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    # Eliminar el archivo temporal del servidor
    os.remove(nombre_archivo)

    return response