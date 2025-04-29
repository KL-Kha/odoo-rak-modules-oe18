{
    "name": "Purchase Agreement notification",
    "summary": "Send notification within 5 days of scheduled date of purchase agreement.",
    "version": "18.0.1.0.0",
    "author": "Parth Tilokani",
    "application": False,
    "depends": ["purchase_requisition"],
    "installable": True,
    "data": [
        "data/ir_cron.xml",
        "data/mail_template.xml",
    ],
}
