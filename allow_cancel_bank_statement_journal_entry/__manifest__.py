#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Block Synchronize Business Models',
    'category': 'Accounting/Accounting',
    'version': '18.0.1.0.0',
    'sequence': 16,
    'author': 'Falinwa China Limited',
    'summary': 'https://www.falinwa.com',
    'description': 
    """
    By using this module to cut down the connection/synchronization between account.move and bank statement details(account.bank.statement.line)
    i.e. Disable "Update the account.bank.statement.line regarding its related account.move" function
    """,
    'depends': [
        'account'
    ],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}