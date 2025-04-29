{
    "name": "Shipping Reminder Notification",
    "summary": "Send notification based on shipping.",
    "version": "18.0.1.0.0",
    "author": "Parth Tilokani",
    "application": False,
    "depends": ["base", "stock", "stock_delivery"],
    "installable": True,
    "data": [
        "data/ir_cron.xml",
        "data/email_template.xml",
    ],
}
