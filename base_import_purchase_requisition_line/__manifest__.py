# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

{
    'name': 'Import Purchase Requisition (Agreement) Lines',
    'version': '18.0.1.0',
    'category': 'Tools',
    'description': """
        Import purchase requisition lines from CSV / Excel file using Odoo native interface
    """,
    'summary': '''
        Import purchase requisition lines from CSV / Excel file using Odoo native interface
    ''',
    'live_test_url': 'https://demo15.domiup.com',
    'author': 'Domiup',
    'price': 25,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    'website': 'https://youtu.be/l6ahS8huo-g',
    'depends': [
        'base_import_line',
        'purchase_requisition',
    ],
    'data': [
        'views/purchase_requisition.xml'
    ],
    'test': [],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'active': False,
    'application': True,
}
