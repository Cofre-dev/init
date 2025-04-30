#Esto es una prueba para ver si el archivo se carga correctamente
from celery import shared_task
from django.core.management import call_command

@shared_task
def get_all_data_task():
    call_command('get_all_data')