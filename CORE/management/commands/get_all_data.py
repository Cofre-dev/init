# CORE/management/commands/get_all_data.py
import requests
import pandas as pd
import os
import sys
from datetime import datetime
from django.core.management.base import BaseCommand
import json

# Configuración
USD_CODE = "F073.TCO.PRE.Z.D"
EURO_CODE = "F072.CLP.EUR.N.O.D"
UF_CODE = "F073.UFF.PRE.Z.D"

API_USER = "rojascofrem@gmail.com"
API_PASS = "Mat.FVC965"

def obtener_ruta_descargas():
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.expanduser("~")
        descargas = os.path.join(base_dir, "Downloads", "IndicadoresBCCH")
        os.makedirs(descargas, exist_ok=True)
        return descargas
    except Exception as e:
        print(f"Error al obtener ruta de descargas: {str(e)}")
        return None

def obtener_datos_bcch(indicador):
    try:
        fecha_inicio = (datetime.now() - pd.DateOffset(months=1)).strftime("%Y-%m-%d")
        fecha_fin = datetime.now().strftime("%Y-%m-%d")
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

        #Esto es un validador para que no se sobreescriba el archivo
        while os.path.exists(ruta_completa):
            ruta_completa = f"{base}_{contador}{extension}"
            contador += 1
        datos.to_excel(ruta_completa, index=False)
        print(f"Archivo guardado exitosamente en: {ruta_completa}")
        return True
    
    except Exception as e:
        print(f"Error al guardar archivo Excel: {str(e)}")
        return False

def procesar_datos(datos):
    if not datos or 'Series' not in datos or 'Obs' not in datos['Series']:
        return None
    df = pd.DataFrame(datos['Series']['Obs'])
    df = df.drop(columns=['statusCode'], errors='ignore') #Eliminar la columna statusCode si existe
    df = df.rename(columns={
        'indexDateString': 'Fecha',
        'value': 'Valor'
    })
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    return df

class Command(BaseCommand):
    help = 'Obtiene y guarda los datos de Dolar, Euro y UF del Banco Central'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando descarga de datos de todos los indicadores...'))

        indicadores = {
            "Dolar": USD_CODE,
            "Euro": EURO_CODE,
            "UF": UF_CODE,
        }

        for nombre, codigo in indicadores.items():
            self.stdout.write(self.style.SUCCESS(f'Descargando datos de {nombre}...'))
            datos = obtener_datos_bcch(codigo)
            if not datos:
                self.stdout.write(self.style.ERROR(f'No se recibieron datos válidos de la API para {nombre}'))
                continue

            # Esto imprime la estructura del JSON 
            if nombre == "Dolar":
                self.stdout.write(self.style.WARNING(f'Estructura JSON de la API para Dolar: {json.dumps(datos, indent=4)}'))

            df = procesar_datos(datos)
            if df is None:
                self.stdout.write(self.style.ERROR(f'Estructura de datos inesperada para {nombre}'))
                continue

            nombre_archivo = f"{nombre.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            if guardar_excel(df, nombre_archivo):
                self.stdout.write(self.style.SUCCESS(f'Datos de {nombre} guardados exitosamente'))
            else:
                self.stdout.write(self.style.ERROR(f'Error al guardar el archivo Excel para {nombre}'))

        self.stdout.write(self.style.SUCCESS('Proceso de descarga de todos los indicadores completado.'))