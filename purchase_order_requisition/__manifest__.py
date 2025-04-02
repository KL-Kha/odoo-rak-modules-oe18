# -*- coding: utf-8 -*-
{
    'name': 'Purchase Requisition',
    'version': '1.0',
    'category': 'account',
    'sequence': 16,
    'summary': 'Default Today Invoice Date',
    'description': "Accounting",
    'author': 'Bipin Prajapati',
    'depends': [
        'purchase_requisition', 'purchase'
    ],
    'data': [
        'views/purchase_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
