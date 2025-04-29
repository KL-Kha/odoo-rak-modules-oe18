# -*- coding: utf-8 -*-
{
    'name': 'Product Battery Info',
    'version': '1.0',
    'category': 'Sale',
    'summary': 'Product Battery Info',
    'description': """
This module Product Battery Info
======================================.
    """,
    'depends': ['sale_management', 'stock', 'purchase'],
    'data': [
        'views/product_view.xml',
        'views/sale_order_view.xml',
        # 'views/purchase_view.xml',
        'views/stock_view.xml',
    ],
    'demo':[
        
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
