# -*- coding: utf-8 -*-
{
    'name': 'Remove tax on portal',
    'version': '1.0',
    'category': 'Sale',
    'summary': 'Remove tax on portal',
    'description': """
Remove tax on portal
======================================.
    """,
    'depends': ['base', 'sale','website_sale','sale_management'],
    'data': [
        'views/sale_view.xml',
    ],
    'demo':[
        
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}
