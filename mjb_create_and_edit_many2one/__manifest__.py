# -*- coding: utf-8 -*-
{
    'name': 'MJB - Create and Edit Many2one Feature Restriction',
    'version': '18.0.0.1',
    'author': 'Majorbird',
    'website': 'https://majorbird.cn',
    'category': 'Tools',
    'summary': 'Restrict Create and Edit in Many2One Fields',
    'description': '''
        This module contain some functions:\n
        1. Restrict Create and Edit feature in Many2One fields based on user groups\n
        2. Provides granular control over who can create/edit records from Many2One fields\n
    ''',
    'depends': [
        'web'
    ],
    'data': [
        'security/create_and_edit_many2one_security.xml',
    ],
    'css': [],
    'js': [],
    "_documentation": {
        "banner": "banner.png",
        "icon": "icon.png",
        "excerpt": "Granular Control for Many2One Field Access",
        "summary": "Welcome to the Many2One Field Access Control module. This tool provides precise control over who can create and edit records directly from Many2One fields, enhancing data integrity and user access management.",
        "issue": "Solving Access Control Challenges",
        "solution": "The Create and Edit Many2One Feature Restriction module addresses the need for fine-grained control over record creation and editing in Many2One fields. It enables administrators to restrict these capabilities based on user groups.",
        "manual": [
            {
                "title": "Installation",
                "description": "Find the module in your applications list and click 'Install'. After installation, configure the user groups to determine who has create/edit permissions.",
                "images": []
            },
            {
                "title": "Managing Permissions",
                "description": "Assign users to the appropriate groups to control their ability to create and edit records from Many2One fields.",
                "images": []
            }
        ],
        "features": [
            {
                "title": "Group-Based Access Control",
                "description": "Precisely control which users can create or edit records directly from Many2One fields."
            },
            {
                "title": "Universal Application",
                "description": "Works across all Many2One fields in the system, providing consistent access control."
            }
        ]
    },
    "assets": {
        "web.assets_backend": [
            "mjb_create_and_edit_many2one/static/src/js/mjb_create_and_edit_many2one.js",
        ]
    },
    'images': ['static/description/banner_slide.gif'],
    'demo': [],
    'application': False,
    'license': 'OPL-1',
    'installable': True,
}