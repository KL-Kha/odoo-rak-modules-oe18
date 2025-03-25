# -*- coding: utf-8 -*-
{
    'name': "Note Template Engine",
    'version': '18.0.0.0.1',
    'license': 'OPL-1',
    'summary': "Handle Terms and Conditions Template.",
    'sequence': 20,
    'category': 'Tools',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    'description': """
        Handle Terms and Conditions Template.
        ============================================
        Enable user to write terms & conditions template, that can be used across all object. This module only stands as the base, but need another module for it to work
    """,
    'depends': ['base'],
    'data': [
        "security/account_security.xml",
        "security/ir.model.access.csv",
        "views/contract_condition_view.xml",
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
