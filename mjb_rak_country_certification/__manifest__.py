# -*- coding: utf-8 -*-
{
    'name': "Country Certification",
    'summary': """Country Certification""",
    'description': """Country Certification""",
    'author': "Major Bird",
    'license': 'LGPL-3',
    'website': "majorbird.cn",
    'category': 'Uncategorized',
    'version': '18.0.0.0.1',
    'images': [
    ],
    'depends': [
        'base',
        'contacts',
        'sale',
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_country_view.xml',
        'views/mjb_cetrification_view.xml',
    ],
    'demo': [],
    'application': True,
}
