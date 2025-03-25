# -*- coding: utf-8 -*-
{
    "name": "Note Template for Purchase",
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'summary': "add Contract Conditions template on purchase order",
    'category': 'Purchases',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    "description": """
        Terms and Conditions.
        ============================================

        Module to add Contract Conditions on purchase.
    """,
    "depends": ["fal_contract_conditions", 'purchase'],
    "data": [
        "views/purchase_view.xml",
    ],
    'images': [
        'static/description/purchase_condition_screenshot.png'
    ],
    'demo': [
    ],
    'price': 180.00,
    'currency': 'EUR',
    'application': False,
}
