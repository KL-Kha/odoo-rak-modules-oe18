# -*- coding: utf-8 -*-
{
    'name': 'Chart Of Account Rak',
    'version': '18.0.0.1',
    'category': 'account',
    'sequence': 16,
    'summary': 'Chart Of Account Rak',
    'description': "Accounting",
    'author': 'Bipin Prajapati',
    'depends': [
        'account', 'hr'
    ],
    'data': [
        'views/account_view.xml',
        'views/employee_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
