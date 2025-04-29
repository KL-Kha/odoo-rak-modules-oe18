# -*- coding: utf-8 -*-
{
    'name': 'Register Sale Order Payment',
    'version': '18.0.10.0',
    'category': 'sale',
    'sequence': 16,
    'summary': 'Register Sale Order Payment',
    'description': "Sale",
    'author': 'Falinwa China Limited',
    'website': "https://www.falinwa.com",
    'depends': [
        'sale', 'account', 'sale_management'
    ],

    'external_dependencies': {
        'python': [
            'requests',
            # 'tenacity'
        ],
    },

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/advance_payment_view.xml',
        'views/global_channel_ept.xml',
        'views/sale_type_view.xml',
        'views/sale_order_view.xml',
        'views/payment_view.xml',
        'views/picking_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
