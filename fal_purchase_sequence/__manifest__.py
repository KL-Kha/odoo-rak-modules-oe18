{
    "name": "Purchase Order Sequence",
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'summary': 'Add Purchase Sequence',
    'sequence': 61,
    'author': "CLuedoo",
    'category': 'Purchase',
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    "description": """
        Customize for sequence, not only request sequence for Supplier Order number, \
        but also  request sequence for Supplier quotation order number, and after \
        confirm quotation order, field of source document will show the quotation  number.
    """,
    "depends": [
        'purchase'
    ],
    'data': [
        'data/order_sequence.xml',
        'views/purchase_view.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    # 'price': 360.00,
    # 'currency': 'EUR',
    'application': False,
}
