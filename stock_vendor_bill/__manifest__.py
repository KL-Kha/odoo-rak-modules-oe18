# -*- coding: utf-8 -*-
{
    'name': 'Stock Vendor Bill',
    'version': '18.0.0.0.1',
    'category': 'account',
    'sequence': 16,
    'summary': 'Stock Vendor Bill',
    'description': "Accounting",
    'author': 'Falinwa China Limited',
    'website': "https://www.falinwa.com",
    'depends': [
        'stock_account', 'fal_purchase_downpayment', 'account'
    ],
    'data': [
        'views/account_view.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
