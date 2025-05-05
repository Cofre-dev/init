from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
import pandas as pd
import os
from datetime import datetime
import requests
import sys
from django.core.management.base import BaseCommand
from io import BytesIO

# Configuración
UF_CODE = "F073.UFF.PRE.Z.D"
API_USER = "rojascofrem@gmail.com"
API_PASS = "Mat.FVC965"

def obtener_ruta_descargas():
    try:
        if getattr(sys, 'frozen', False):
            # Modo ejecutable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Modo desarrollo
            base_dir = os.path.expanduser("~")

        descargas = os.path.join(base_dir, "Downloads", "IndicadoresBCCH")
        os.makedirs(descargas, exist_ok=True)
        return descargas
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

def guardar_excel(datos, nombre_archivo, output=None):
    try:
        if output:
            datos.to_excel(output, index=False)
            print(f"Archivo guardado en memoria.")
            return True
        else:
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
    help = 'Obtiene y guarda los datos de la UF del Banco Central'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            nargs='?',
            type=BytesIO,
            help='Objeto para escribir la salida del archivo (en memoria)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando descarga de datos del EURO...'))

        fecha_inicio = (datetime.now() - pd.DateOffset(months=1)).strftime("%Y-%m-%d")
        fecha_fin = datetime.now().strftime("%Y-%m-%d")

        datos = obtener_datos_bcch(UF_CODE, fecha_inicio, fecha_fin)
        if not datos:
            self.stdout.write(self.style.ERROR('No se recibieron datos válidos de la API'))
            return

        if 'Series' not in datos or 'Obs' not in datos['Series']:
            self.stdout.write(self.style.ERROR('Estructura de datos inesperada'))
            return

        df = pd.DataFrame(datos['Series']['Obs'])
        df = df.drop(columns=['statusCode'], errors='ignore')
        df = df.rename(columns={
            'indexDateString': 'Fecha',
            'value': 'Valor'
        })

        # Convertir tipos de datos
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

        nombre_archivo = f"UF_{datetime.now().strftime('%Y%m%d')}.xlsx"
        output_file = options.get('output')

        if guardar_excel(df, nombre_archivo, output=output_file):
            self.stdout.write(self.style.SUCCESS('Proceso completado exitosamente'))
        else:
            self.stdout.write(self.style.ERROR('Error al guardar el archivo Excel'))