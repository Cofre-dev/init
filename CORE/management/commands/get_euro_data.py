import requests
import pandas as pd
import os
import sys
from datetime import datetime
from django.core.management.base import BaseCommand 
import json 
import requests

# Configuración
EURO_CODE = "F072.CLP.EUR.N.O.D"
API_USER = "rojascofrem@gmail.com"
API_PASS = "Mat.FVC965"

def obtener_ruta_descargas():
    try:
        # se crea una carpeta temporal para guardar los archivos descargados
        from django.conf import settings
        ruta_temporal = os.path.join(settings.MEDIA_ROOT, "descargas")
        os.makedirs(ruta_temporal, exist_ok=True)
        return ruta_temporal
    except Exception as e:
        print(f"Error al obtener ruta de descargas: {str(e)}")
        return None

def obtener_datos_bcch(indicador, fecha_inicio, fecha_fin):
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

def guardar_excel(datos, nombre_archivo):
    try:
        ruta_descargas = obtener_ruta_descargas()
        if not ruta_descargas:
            return False

        ruta_completa = os.path.join(ruta_descargas, nombre_archivo)

        contador = 1
        base, extension = os.path.splitext(ruta_completa)
        while os.path.exists(ruta_completa):
            ruta_completa = f"{base}_{contador}{extension}"
            contador += 1

        datos.to_excel(ruta_completa, index=False)
        print(f"Archivo guardado exitosamente en: {ruta_completa}")
        return True
    except Exception as e:
        print(f"Error al guardar archivo Excel: {str(e)}")
        return False

class Command(BaseCommand):
    help = 'Obtiene y guarda los datos del EURO del Banco Central'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando descarga de datos del EURO...'))

        fecha_inicio = (datetime.now() - pd.DateOffset(months=1)).strftime("%Y-%m-%d")
        fecha_fin = datetime.now().strftime("%Y-%m-%d")

        datos = obtener_datos_bcch(EURO_CODE, fecha_inicio, fecha_fin)
        if not datos:
            self.stdout.write(self.style.ERROR('No se recibieron datos válidos de la API'))
            return

        if 'Series' not in datos or 'Obs' not in datos['Series']:
            self.stdout.write(self.style.ERROR('Estructura de datos inesperada'))
            return

        df = pd.DataFrame(datos['Series']['Obs'])
        df = df.drop(columns=['statusCode'], errors='ignore') #Eliminar la columna statusCode si existe
        df = df.rename(columns={
            'indexDateString': 'Fecha',
            'value': 'Valor'
        })

        # Convertir tipos de datos
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

        nombre_archivo = f"DOLAR_{datetime.now().strftime('%Y%m%d')}.xlsx"

        if guardar_excel(df, nombre_archivo):
            self.stdout.write(self.style.SUCCESS('Proceso completado exitosamente'))
        else:
            self.stdout.write(self.style.ERROR('Error al guardar el archivo Excel'))

