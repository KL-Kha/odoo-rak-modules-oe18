# -*- coding: utf-8 -*-
{
    'name': 'Domain restriction for internal & public users',
    'author': "Majorbird",
    'website': "https://majorbird.cn/",
    'version': '18.0.0.1',
    'category': 'Base',
    'summary': 'Internal and External Domain',
    'description': """
        This module allows you to restrict access to Odoo as follows:
        - Internal users: can only login from the internal domain (example: internal.domain.com)
        - Public users and Portal users: can only login from the external domain (example: external.domain.com)
        - Public users and Portal users: cannot access shared documents from internal domain
    """,
    'depends': ['base', 'portal', 'mail', 'base_automation'],
    'data': [
        'data/auto_email_replace_body.xml'
    ],
    'demo': [],
    'images': [
        'static/description/app_screenshot.png'
    ],
    'price': '50.00',
    'currency': 'USD',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    'auto_install': False,
}
