{
    "name": "Subcontracting Cost Allocation for Manufacturing Order",  
    "author": "Majorbird",
    "version": "0.1",
    "category": "Inventory/Inventory",
    "summary": "This module is an all-encompassing tool for efficiently managing and dividing subcontracting costs in a production environment. The module simplifies the process of determining, allocating, and tracking costs associated with each manufacturing order.",  
    "website": "majorbird.cn",
    "depends": [
        "base",
        "stock",
        "account",
        "mrp",
        "mrp_maintenance",
        "base_automation",
        "stock_account"
    ],
    "data": [
        'data/action.xml',
        'data/base_automation.xml',
        'views/product_category_views.xml',
    ],
    "_documentation": {  
        "banner": "",  
        "icon": "",  
        "excerpt": "This module provides a robust solution for efficiently managing and allocating subcontracting costs in manufacturing orders.",  
        "summary": "The 'Subcontracting Cost Allocation for Manufacturing Orders' module introduced by MajorBird is an all-encompassing tool for efficiently managing and dividing subcontracting costs in a production environment. The module simplifies the process of determining, allocating, and tracking costs associated with each manufacturing order. Equipped with this module, organizations can accurately estimate manufacturing order costs, ensuring financial transparency and aiding in important financial decision-making.",  
        "issue": "Subcontracting costs can be complex to manage, often varying with each manufacturing order. Therefore, they are difficult to accurately allocate and track in financial records.",  
        "solution": "The module helps combat these issues by providing a direct, simplified method for dividing subcontracting costs per manufacturing order. It allows users to define cost parameters on a per-product-category basis and efficiently calculate the divided costs.",  
        "manual": [  
            {  
            "title": "Installation",  
            "description": "To install, navigate to the Apps module and search for 'Subcontracting Cost Allocation for Manufacturing Order'",  
            "images": ['image1.png']
            },
            {  
            "title": "Before Configuration",  
            "description": "Once installed the Subcontracting Cost Allocation for Manufacturing Order, make sure we also have the Purchase Application and the MRP Application. Turn on the Subcontracting on the Manufaturing Settings to allow sub split service.",  
            "images": ['image2_1.png','image2_2.png']
            },
            {  
            "title": "Configuration",  
            "description": "Once we have all we needed, configurations can be performed through the product category and configuration for SubContract Valuation Account and SubContract Material Account.",  
            "images": ['image3_1.png','image3_2.png']
            },
            {  
            "title": "Let The Code Do Their Job!",  
            "description": "Continue to make a purchase and confirm the purchase. Finally we can check the result in the Journal Entries.",  
            "images": ['image4_1.png']
            },
        ],  
        "features": [  
            {  
            "title": "Efficient Subcontracting Cost Management",  
            "description": "The system effortlessly handles the complexity of subcontracting cost allocation in manufacturing orders, providing precise and easily trackable information.",  
            },  
            {  
            "title": "Flexible Configuration",  
            "description": "Allows flexibility in assigning cost parameters based on the product category, ensuring the cost reflect actual manufacturing costs.",  
            },  
        ],  
    }, 
    'images': ['static/description/banner_slide.gif'],
    "license": "OPL-1",
    "installable": True,
    "images": [],
}
