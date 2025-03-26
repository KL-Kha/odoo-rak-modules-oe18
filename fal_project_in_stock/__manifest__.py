# encoding: utf-8
# Part of Odoo - CLuedoo Edition. Ask Falinwa / CLuedoo representative for full copyright And licensing details.
{
    'name': 'Analytic Account in Stock',
    "version": "18.0.1.0.0",
    'license': 'OPL-1',
    'summary': 'Module to define a Analytic Account in stock.',
    'sequence': 100,
    'category': 'Inventory',
    'author': 'CLuedoo',
    'website': 'https://www.cluedoo.com',
    'support': 'cluedoo@falinwa.com',
    "description": """
        Analytic Account in Stock
        =========================================

        Module to add Analytic account and additional field on stock.
    """,
    'depends': [
        'stock_account',
    ],
    'init_xml': [],
    'data': [
        'views/stock_view.xml',
    ],
    'images': [
        'static/description/pipp_screenshot.png'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'price': 180.00,
    'currency': 'EUR',
    'installable': True,
    'active': False,
    'application': False,
    'auto_install': False,
    'post_init_hook': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
