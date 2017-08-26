import html
import json
import re

import copy
import requests
from django.core.management.base import BaseCommand

# For byensburger we've used:
# .manage.py food_json byensburger -ec 3983 3758 283 4048 228 48 135 247 -ep 2220636 2220652 2220653 2220654 2220658
# Which will output
# Excluded categories 3983 - Tilbud, 3758 - Chokolade & Slik, 283 - Chips, 4048 - Nyheder,
#   228 - Børne Burgere, 48 - Vine, 135 - Spiritus -min. 18 år, 247 - Diverse
# Excluded products 2220652 - Øl (Carlsberg), 2220653 - Øl (Heineken), 2220654 - Øl (Tuborg),
#   2220658 - Husets vin, 2220636 - Chilisauce - License to Eat


class Command(BaseCommand):
    help = 'Loads food from just eat'

    menu = None

    def add_arguments(self, parser):
        parser.add_argument('restaurant', nargs=1, type=str)
        parser.add_argument('--exclude-categories', '-ec', nargs='+', type=int, dest='categories')
        parser.add_argument('--exclude-products', '-ep', nargs='+', type=int, dest='products')
        parser.add_argument('--list', action='store_true', dest='list', default=False)

    def del_product(self, product):
        for i, item in enumerate(self.menu['products']):
            if item.get('Id', 0) == product['Id']:
                self.menu['products'][i] = {}
                break

    def get_product_name(self, product):
        actual_product = next((item for item in self.menu['products'] if item.get('Id', 0) == product['Id']), None)
        name = actual_product['Name']
        if actual_product['Syn']:
            name += ' ({})'.format(actual_product['Syn'])
        return name

    def handle(self, *args, **options):
        print(options['restaurant'])
        r = requests.get('https://www.just-eat.dk/restaurants-byensburger/menu'.format(options['restaurant']))
        print(r.status_code)
        if r.status_code != 200:
            print("Error")
            print(r.text)
        data = r.text
        search = re.search(r'<div class=\"menu\" data-menu=\'([^\'\v]*)\'', data)
        if not search:
            print('Error, could not find menu')
        data = search.group(1)
        data = html.unescape(data)
        self.menu = json.loads(data)['Menu']

        if options['list']:
            for category in self.menu['Categories']:
                print('{} - {}'.format(category['Id'], category['Name']))
                for item in category['Items']:
                    for product in item['Products']:
                        print('\t{} - {}'.format(product['Id'], self.get_product_name(product)))
        else:
            excluded_categories = []
            excluded_products = []
            for i, category in enumerate(copy.deepcopy(self.menu)['Categories']):
                if category['Id'] in options['categories']:
                    excluded_categories.append('{} - {}'.format(category['Id'], category['Name']))
                    self.menu['Categories'][i] = {}

                for j, item in enumerate(category['Items']):
                    for k, product in enumerate(item['Products']):
                        if product['Id'] in options['products']:
                            excluded_products.append('{} - {}'.format(product['Id'], self.get_product_name(product)))
                            self.menu['Categories'][i]['Items'][j]['Products'][k] = {}

                        if product['Id'] in options['products'] or category['Id'] in options['categories']:
                            self.del_product(product)

            # Clean out descriptions
            for i, product in enumerate(self.menu['products']):
                if product:
                    self.menu['products'][i]['Desc'] = ''

            print('Excluded categories', ', '.join(excluded_categories))
            print('Excluded products', ', '.join(excluded_products))

            with open('main/static/main/food.json', 'w') as f:
                json.dump({'Menu': self.menu}, f, separators=(',', ':'), indent=None)
