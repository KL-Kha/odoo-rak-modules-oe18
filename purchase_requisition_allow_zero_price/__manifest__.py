# encoding: utf-8
# Author: Majorbird
{
    "name": "Purchase Requisition - Allow Zero Price in Purchase Requisition Line",
    "version": "18.0.0.1",
    'license': 'OPL-1',
    'summary': 'This module adds features.',
    'sequence': 18,
    'category': 'Purchase',
    'author': 'Majorbird',
    'website': 'https://majorbird.cn',
    'support': 'odoo@majorbird.cn',
    "description": """
        Purchase Requisition - Allow Zero Price in Purchase Requisition Line
        ======================================================
    """,
    'depends': [
        'purchase', 'purchase_stock', 'purchase_requisition'
    ],
    'init_xml': [],
    'data': [],
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