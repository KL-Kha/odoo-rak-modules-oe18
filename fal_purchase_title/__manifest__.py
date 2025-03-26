# -*- coding: utf-8 -*-
{
    'name': "Purchase Title",
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'summary': "Purchase Order : Title",
    'category': 'Purchases',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',

    'description': """
        Purchase Order : Title
        ChangeLog :
        12.1.0.0.0 - Initial Release
    """,

    'depends': ['purchase', 'fal_invoice_title'],

    'data': [
        'views/purchase_views.xml',
    ],
    'images': [
        'static/description/fal_purchase_additional_info_screenshot.png'
    ],
    'demo': [
    ],
    'installable': True,
    'price': 270.00,
    'currency': 'EUR',
}
