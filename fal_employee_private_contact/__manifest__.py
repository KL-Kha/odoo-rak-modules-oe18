# -*- coding: utf-8 -*-
{
    'name': "Employee Private Address",
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'summary': """Create private contact when create employee""",
    'category': 'Partner Management',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com/",
    'support': 'cluedoo@falinwa.com',
    'description': """
        Employee Private Address
        =========================

        Force the employee address to be of type private when creating employee info
    """,
    'depends': ['hr', 'fal_partner_private_address'],
    'data': [
        'views/hr_employee.xml',
    ],
    'images': [
        'static/description/employee_private_screenshoot.png'
    ],
    'demo': [
    ],
    'price': 180.00,
    'currency': 'EUR',
    'application': False,
}
