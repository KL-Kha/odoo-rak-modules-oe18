{
    "name": "PO RFQ Notification",
    "summary": "Send notification on RFQ if it is delayed to 3 days.",
    "version": "18.0.1.0.0",
    "author": "Parth Tilokani",
    "application": False,
    "depends": ["purchase"],
    "installable": True,
    "data": [
        "data/ir_cron.xml",

    ],
}
