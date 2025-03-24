{
    "name": "Quantity-Limited Stock Control",
    "author": "Majorbird",
    "version": "18.0.0.1",  
    "category": "inventory",
    "summary": "Control received quantity not exceeding the permissible limit.",
    "website": "https://majorbird.cn",
    "depends": [
        'base','base_automation','stock','base_automation','utm','mail'
    ],''
    "data": [
        'security/ir.model.access.csv',
        'data/server_action.xml',
        'data/automated_action_data.xml',
        
        'views/order_qty_done_limit.xml',
    ],
    "_documentation": {
        "banner": "banner.png",
        "icon": "icon.png",
        "excerpt": "Manage stock quantities with quantity limits to ensure control and compliance.",
        "summary": "The Quantity-Limited Stock Control module provides enhanced control over your inventory by enforcing quantity limits for received items. This module helps you maintain accurate stock levels by preventing quantities from exceeding permissible limits. It integrates seamlessly with Odoo's stock management, allowing you to configure and enforce quantity limits for your products with ease.",
        "issue": "Inventory management can become challenging when quantities of received items exceed permissible limits, leading to discrepancies and compliance issues.",
        "solution": "The Quantity-Limited Stock Control module offers a simple yet effective solution to manage stock quantities by setting and enforcing limits. It ensures that your inventory stays within compliance, preventing overstocking and potential issues associated with it.",
        "manual": [
            {
                "title": "Installation",
                "description": "1. Locate the module in the Odoo application list.\n2. Click 'Install' to begin the installation process.",
                "images": ["image1.png"]
            },
            {
                "title": "Configuring Quantity Limits",
                "description": "1. Navigate to 'Inventory' > 'Configuration' > 'Quantity-Limited Stock Control'.\n2. Create and configure quantity limits for your products.",
                "images": ["image2.png"]
            },
            {
                "title": "Active The Operation",
                "description": "Make sure active the operation before testing for the result!",
                "images": ["image3.png"]
            },
            {
                "title": "Enforcing Quantity Limits",
                "description": "1. As items are received into stock, the module will automatically check and enforce quantity limits.\n2. Any attempts to exceed the limits will trigger warnings or prevent further stock movements.",
                "images": ["image4.png"]
            },
        ],
        "features": [
            {
                "title": "Quantity Limit Enforcement",
                "description": "This module enables you to set and enforce quantity limits for each product in your inventory."
            },
            {
                "title": "Integration with Stock Management",
                "description": "Seamless integration with Odoo's stock management ensures that quantity limits are applied throughout your inventory operations."
            },
            {
                "title": "Control and Compliance",
                "description": "Maintain control over your stock quantities to prevent overstocking and compliance issues."
            },
        ]
    },
    'images': [
        'static/description/banner_slide.gif'
    ],
    'currency': 'USD',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    'auto_install': False,
}
