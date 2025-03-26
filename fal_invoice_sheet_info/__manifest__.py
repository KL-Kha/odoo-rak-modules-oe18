# -*- coding: utf-8 -*-
{
    'name': "Invoice List on Sale and Purchase.",
    "version": "18.0.0.0.1",
    'license': 'OPL-1',
    'summary': "List of Invoice in Sale and Purchase.",
    'sequence': 20,
    'category': 'Accounting & Finance',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    'description': """
        List of Invoice in Sale and Purchase.
        =========================================
        Add Invoices Information on Sales & Purchase Form
    """,
    'depends': ['account', 'purchase', 'sale_management'],
    'data': [
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ],
    'images': [
        'static/description/sale_order_screenshot.png'
    ],
    'demo': [
    ],
    'price': 180.00,
    'currency': 'EUR',
    'application': False,
}
