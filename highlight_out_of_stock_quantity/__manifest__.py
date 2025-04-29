# -*- coding: utf-8 -*-
{
    'name': 'Highlight Out of Stock Quantity',
    'version': '1.0',
    'category': 'Stock',
    'summary': ' Highlight Out of Stock Quantity',
    'description': """
This module Highlight Out of Stock Quantity
======================================.
    """,
    'depends': ['stock', 'web', 'account_accountant', 'mrp'],
    'data': [
        'views/stock_view.xml',
        'views/account_view.xml',
        'views/manufacturing_view.xml',
        'wizard/ac_move_reversal_inherit_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'highlight_out_of_stock_quantity/static/src/css/style.css',
        ]},
    'application': True,
    'installable': True,
    'auto_install': False,
}
