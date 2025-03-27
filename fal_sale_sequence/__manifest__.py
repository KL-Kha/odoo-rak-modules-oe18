# -*- coding: utf-8 -*-
{
    'name': "Quotation & Sales Order Sequence.",
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'summary': "Sequence in Quotation & Sales Order.",
    'sequence': 20,
    'category': 'Sales',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    'description': """
        Sequence in Quotation & Sales Order.
        ====================================================
        Customize for sequence, not only request sequence for Customer Order number, 
        but also  request sequence for Customer quotation order number, and after
        confirm quotation order, field of source document will show the quotation  number.
    """,
    'depends': ['sale'],
    'data': [
        'data/order_sequence.xml',
        'views/sale_view.xml'
    ],
    'images': [
        'static/description/1_screenshot.png'
    ],
    'demo': [
    ],
    'price': 180.00,
    'currency': 'EUR',
    'application': False,
}
