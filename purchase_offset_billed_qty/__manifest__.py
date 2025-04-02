# encoding: utf-8
# Author: Majorbird
{
    "name": "Purchase - Offset Billed Qty",
    "version": "18.0.0.1",
    'license': 'OPL-1',
    'summary': 'This module adds features.',
    'sequence': 18,
    'category': 'Sales',
    'author': 'Majorbird',
    'website': 'https://majorbird.cn',
    'support': 'odoo@majorbird.cn',
    "description": """
        Purchase - Offset Billed Qty
        ======================================================
    """,
    'depends': [
        'sale_purchase',
        'purchase_stock'
    ],
    'init_xml': [],
    "data": [
        "views/purchase_order_line_views.xml"
    ],
    'images': [
        # 'static/description/mrp_ext_screenshot.png'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'price': 0.00,
    'currency': 'EUR',
    'installable': True,
    'active': False,
    'application': False,
    'auto_install': False,
    'post_init_hook': '',
}