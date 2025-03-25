# -*- coding: utf-8 -*-
{
    "name": "Note template for Sales",
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'summary': "add Contract Conditions template on sale order",
    'category': "Sales",
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    "description": """
        Terms and Conditions.
        ============================================

        Module to add Contract Conditions on sale.
    """,
    "depends": ["fal_contract_conditions", "sale_management"],
    "data": [
        "views/sale_view.xml",
    ],
    'images': [
        'static/description/sale_condition_screenshot.png'
    ],
    'demo': [
    ],
    'price': 180.00,
    'currency': 'EUR',
    'application': False,
}
