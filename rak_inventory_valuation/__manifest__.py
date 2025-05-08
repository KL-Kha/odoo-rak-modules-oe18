# -*- coding: utf-8 -*-
{
    "name": "rak inventory",
    "website": "",
    "support": "",
    "category": "Inventory Valuation",
    "summary": "mo For RAK Technology",
    "version": "18.0.0.0",
    "depends": [
        'stock_account','account','stock',
    ],
    "application": True,
    "data": [
        'security/ir.model.access.csv',
        'views/stock_valuation.xml',

    ],

    "auto_install": False,
    "installable": True,

}

