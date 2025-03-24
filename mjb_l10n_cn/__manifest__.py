# -*- coding: utf-8 -*-
# Part of Odoo Majorbird Edition.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'China - Accounting',
    'version': '18.0.0.1',
    'license': 'OPL-1',
    'author': 'Majorbird',
    'website': "https://www.odoo.com",
    'category': 'Accounting/Localizations/Account Charts',
    'summary': 'Manage the accounting chart (with hierarchy) for China',
    'support': 'odoo@majorbird.cn',
    'description': """
This is the module to manage
the accounting chart (with hierarchy) for China in Odoo.
(China COA)
""",
    'depends': [
        'base',
        'base_automation',
        'account',
        'account_accountant',
    ],
    'data': [
        'data/account_chart_type.xml',
        'data/automated_action_data.xml',
        'views/account_chart_type_views.xml',
    ],
    "_documentation": {
        "banner": "banner.png",
        "icon": "icon.png",
        "excerpt": "Streamline Your Accounting in China",
        "summary": "The China Accounting module for Odoo empowers businesses to efficiently manage their accounting chart with hierarchy, specifically tailored for the Chinese market.",
        "issue": "Complex Accounting Requirements in China",
        "solution": "This module addresses the complex accounting needs of Chinese businesses by providing a comprehensive accounting chart with a hierarchical structure. It simplifies financial management and reporting, enabling you to meet regulatory and compliance standards with ease.",
        "manual": [
            {
                "title": "Installation",
                "description": "Locate the module in the application list and proceed with clicking 'Install'!",
                "images": ["image1.png"]
            },
            {
                "title": "Configuration",
                "description": "Configure the module settings to align with your specific accounting requirements in China.",
                "images": ["image2.png"]
            }
        ],
        "features": [
            {
                "title": "Chinese Chart of Accounts Management",
                "description": "Effortlessly manage the Chinese Chart of Accounts (CoA) with a hierarchical structure, ensuring accurate financial reporting."
            },
            {
                "title": "Compliance",
                "description": "Stay compliant with Chinese accounting standards and regulations, simplifying tax reporting and auditing."
            }
        ]
    },
    'price': 360.00,
    'currency': 'EUR',
    'application': False,
    'images': ['static/description/banner_slide.gif'],
}
