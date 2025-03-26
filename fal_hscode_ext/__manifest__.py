# -*- coding: utf-8 -*-
{
    "name": "HS Code",
    "version": "18.0.0.0.1",
    'category': "Inventory",
    'author': 'CLuedoo',
    'license': 'LGPL-3',
    'website': 'https://www.cluedoo.com',
    'support': 'cluedoo@falinwa.com',
    'summary': 'Provide HS Code on Product Category Level',
    "description": """
        Provide HS Code on Product Category Level
        =====================================================

        This module provide HS code on Product Category level, so
        we can use it on printing HS Code on invoice, purchase, sale
        and delivery report.
    """,
    "depends": [
        'stock',
        'sale_stock',
        'stock_delivery',
        'purchase',
        'sale',
        'account',
        'delivery'
    ],
    'init_xml': [],
    'data': [
        'views/product_view.xml',
        'views/report_deliveryslip.xml'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
