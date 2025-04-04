from . import models
LEGACY_DATA = {}


def pre_init_hook(env):
    partners = env['res.partner'].search([
        '|',
        ('property_payment_term_id', '!=', False),
        ('property_supplier_payment_term_id', '!=', False),
    ])
    for partner in partners:
        LEGACY_DATA[partner.id] = {
            'property_payment_term_id': partner.property_payment_term_id.id,
            'property_supplier_payment_term_id': partner.property_supplier_payment_term_id.id,
        }
        partner.property_payment_term_id = False
        partner.property_supplier_payment_term_id = False

def post_init_hook(env):
    partners = env['res.partner'].browse(list(LEGACY_DATA.keys()))
    for partner in partners:
        payment_term_id = LEGACY_DATA[partner.id]['property_payment_term_id']
        supplier_payment_term_id = LEGACY_DATA[partner.id]['property_supplier_payment_term_id']
        if payment_term_id:
            partner.property_payment_term_id = payment_term_id
        if supplier_payment_term_id:
            partner.property_supplier_payment_term_id = supplier_payment_term_id

def uninstall_hook(env):
    partners = env['res.partner'].search([
        '|',
        ('property_payment_term_id', '!=', False),
        ('property_supplier_payment_term_id', '!=', False),
    ])
    # for partner in partners:
    #     partner.property_payment_term_id = LEGACY_DATA[partner.id]['property_payment_term_id']
    #     partner.property_supplier_payment_term_id = LEGACY_DATA[partner.id]['property_supplier_payment_term_id']
