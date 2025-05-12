# -*- coding: utf-8 -*-
{
    'name': "Validation process.",
    'version': '17.0.0.1',
    'license': 'OPL-1',
    'summary': "Enable Dynamic Validation Process.",
    'sequence': 20,
    'category': 'Tools',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    'description': """
        Enable Dynamic Validation Process.
        ===============================================================
        Enable Dynamic Process for Records Validation. This function can be done on any kind of records, and can be dynamically changed
    """,
    'depends': [
                'web',
                'mail'],
    'data': [
        "security/ir.model.access.csv",
        # 'views/assets.xml',
        'views/fal_vprocess.xml',
        'views/fal_vprocess_step.xml',
        'views/fal_vprocess_rule.xml',
        'views/fal_vprocess_execution.xml',
        'views/ir_filters.xml',
    ],
    'images': [
    ],
    'demo': [
    ],
    'price': 630.00,
    'currency': 'EUR',
    'application': False,
    "assets": {
        "web.assets_qweb": [
            # "validation_process/static/src/xml/*.xml",
        ],
        "web.assets_backend": [
            "validation_process/static/src/scss/Falinwa/falinwa.scss",
            "validation_process/static/src/js/Falinwa/Falinwa.config.js",
            "validation_process/static/src/js/Falinwa/Falinwa.helper.js",
            "validation_process/static/src/js/Falinwa/Falinwa.queryEngine.js",
            "validation_process/static/src/js/Falinwa/Falinwa.validationProcess.js",
            "validation_process/static/src/js/Falinwa/Falinwa.js",
        ],
    },
}
