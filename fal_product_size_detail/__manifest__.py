# encoding: utf-8
# Part of Odoo - CLuedoo Edition. Ask Falinwa / CLuedoo representative for full copyright And licensing details.
{
    'name': "Product Detailed Specification",
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'summary': 'Add details in product',
    'sequence': 13,
    'category':'Product',
    'author': "CLuedoo",
    'website': 'https://www.cluedoo.com',
    'support': 'cluedoo@falinwa.com',
    "description": """
This module has features
=========================

1. Add details on product. Currently stil size (length, width, and height).
2. New UoM milimeter.
    """,
    'depends': [
      'stock',
    ],
    'data': [
      'data/product_data.xml',
      'views/product_view.xml',
    ],
    'images': [],
    'demo': [],
    # 'price': 360.00,
    'currency': 'EUR',
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
