# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

{
    'name': 'Import Stock Picking Line (Stock Move)',
    'version': '18.0.1.0',
    'category': 'Tools',
    'description': """
        Import stock picking lines from CSV / Excel file using Odoo native interface 
    """,
    'summary': '''
        Import stock picking lines from CSV / Excel file using Odoo native interface
    ''',
    'live_test_url': 'https://demo15.domiup.com',
    'author': 'Domiup',
    'price': 25,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    'website': 'https://youtu.be/rWpNH2jgZBE',
    'depends': [
        'base_import_line',
        'stock',
    ],
    'data': [
        'views/pickings.xml'
    ],

    'test': [],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'active': False,
    'application': True,
}
