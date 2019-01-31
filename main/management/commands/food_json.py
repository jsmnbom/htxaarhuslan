import json

import copy
import requests
from django.core.management.base import BaseCommand

# Use "./manage.py help food_json" for help on how to use this script!

# Please update this on next use:
# (it shows the command we last used)
#
# ./manage.py food_json 1066 -ec 3977 3758 283 163 3 48 135 247
#                             -ep 2779663 2779666 2779667 2779668 2779669 2779650
# Which output
# Excluded categories 3977 - Super Bowl, 3758 - Chokolade & Slik, 283 - Chips, 163 - Snacks, 3 - Desserter,
#       48 - Vine, 135 - Spiritus -min. 18 år, 247 - Diverse
# Excluded products 2779663 - Red Bull, 2779666 - Øl (Carlsberg), 2779667 - Øl (Heineken), 2779668 - Øl (Tuborg),
#       2779669 - Husets vin, 2779650 - Chilisauce - License to Eat

CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
JUST_EAT_MENU_URL = 'https://www.just-eat.dk/menu/getproductsformenu'

HELP = """
Loads food data from just eat

Needs a menuId, find it by going to a menu page on just-eat.dk and opening the developer console and executing:
JustEatData.MenuId

To find category and product ids execute:
document.querySelectorAll('.menuCard-category').forEach(function (c) {console.log(c.querySelector('h3').textContent.trim(), c.dataset.categoryId);c.querySelectorAll('.menu-product').forEach(function (p) {console.log('    ', p.querySelector('h4').textContent.trim(), p.dataset.productId);})})
"""


class Command(BaseCommand):
    help = HELP

    menu = None

    def add_arguments(self, parser):
        parser.add_argument('menuId', nargs=1, type=str)
        parser.add_argument('--exclude-categories', '-ec', nargs='+', type=int, dest='categories')
        parser.add_argument('--exclude-products', '-ep', nargs='+', type=int, dest='products')

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
        r = requests.get(JUST_EAT_MENU_URL,
                         params={'menuId': options['menuId']},
                         headers={'User-Agent': CHROME_USER_AGENT})
        print(r.status_code)
        if r.status_code != 200:
            print("Error")
            print(r.text)
        self.menu = r.json()['Menu']

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
