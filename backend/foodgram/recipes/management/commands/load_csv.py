import csv

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient, Tag

ALREDY_LOADED_ERROR_MESSAGE = 'The database is already loaded.'

ingredients_file = f'{settings.BASE_DIR}/data/ingredients.csv'
tags_file = f'{settings.BASE_DIR}/data/tags.csv'

CSV_DATA = {Ingredient: ingredients_file,
            Tag: tags_file}


class Command(BaseCommand):
    """Загрузка готовой базы данных для моделей Ingredient
    и Tag."""
    help = "Loads data from csv files"

    def handle(self, *args, **kwargs):
        for model, csv_file in CSV_DATA.items():
            if model.objects.exists():
                print(ALREDY_LOADED_ERROR_MESSAGE)
                return

            with open(csv_file, encoding='utf-8') as file:
                reader = csv.reader(file)
                for id, row in enumerate(reader):
                    data = model(id+1, *row)
                    data.save()
