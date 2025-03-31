# -*- coding: utf-8 -*-

{
    'name': 'Message Teams In SO',
    'version': '18.0.0.2',
    'summary': """Sales team can inform staff in PMC/PACKING or Logistics with data from SO.""",
    'description': """Sales team can inform staff in PMC/PACKING or Logistics with data from SO.""",
    'category': 'Sale',
    'sequence': 1,
    'author': '深圳丹鸟网络科技有限公司',
    'website': "https://majorbird.cn",
    'license': 'Other proprietary',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/message_team_views.xml',
        'views/sale_order_views.xml',
    ],
    'qweb': [],
    'images': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
