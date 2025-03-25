# -*- coding: utf-8 -*-
{
    "name": "Note template for Invoice",
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'summary': "add Contract Conditions template on invoice",
    'category': 'Invoicing Management',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    "description": """
        Terms and Conditions.
        ============================================

        Module to add Contract Conditions on Invoice.
    """,
    "depends": ["fal_contract_conditions", 'account'],
    "data": [
        "views/account_invoice_view.xml",
    ],
    'images': [
        'static/description/invoice_condition_screenshot.png'
    ],
    'demo': [
    ],
    'price': 180.00,
    'currency': 'EUR',
    'application': False,
}
