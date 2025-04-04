from . import models

LEGACY_DATA = {}


def pre_init_hook(env):

    table = env['res.partner']._table

    # Step 1: Check column type
    env.cr.execute("""
        SELECT data_type
        FROM information_schema.columns
        WHERE table_name = %s
          AND column_name = 'property_payment_term_id'
    """, (table,))
    field_type = env.cr.fetchone()[0]

    if field_type != 'jsonb':
        return

    # Step 2: Create temporary backup table
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

    # Step 4: Nullify data before changing the column type
    env.cr.execute(f"""
        UPDATE {table}
        SET property_payment_term_id = NULL,
            property_supplier_payment_term_id = NULL
        WHERE property_payment_term_id IS NOT NULL
           OR property_supplier_payment_term_id IS NOT NULL
    """)

    # Step 5: Convert JSONB columns to INTEGER, with safe casting
    env.cr.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN property_payment_term_id DROP DEFAULT,
        ALTER COLUMN property_payment_term_id TYPE integer
        USING CASE
            WHEN property_payment_term_id ? (company_id::text)
            THEN (property_payment_term_id ->> (company_id::text))::integer
            ELSE NULL
        END,
        ALTER COLUMN property_payment_term_id SET DEFAULT NULL
    """)

    env.cr.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN property_supplier_payment_term_id DROP DEFAULT,
        ALTER COLUMN property_supplier_payment_term_id TYPE integer
        USING CASE
            WHEN property_supplier_payment_term_id ? (company_id::text)
            THEN (property_supplier_payment_term_id ->> (company_id::text))::integer
            ELSE NULL
        END,
        ALTER COLUMN property_supplier_payment_term_id SET DEFAULT NULL
    """)

    env.cr.commit()


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
    table = env['res.partner']._table

    # Step 1: Check current column type
    env.cr.execute(f"""
        SELECT data_type
        FROM information_schema.columns
        WHERE table_name = %s
          AND column_name = 'property_payment_term_id'
    """, (table,))
    field_type = env.cr.fetchone()[0]

    if field_type == 'jsonb':
        return

    # Step 2: Drop foreign key constraints

    env.cr.execute(f"""
        ALTER TABLE {table} DROP CONSTRAINT IF EXISTS res_partner_property_payment_term_id_fkey
    """)
    env.cr.execute(f"""
        ALTER TABLE {table} DROP CONSTRAINT IF EXISTS res_partner_property_supplier_payment_term_id_fkey
    """)

    # Step 3: Alter column to JSONB with safe NULL handling
    env.cr.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN property_payment_term_id DROP DEFAULT,
        ALTER COLUMN property_payment_term_id TYPE jsonb
        USING CASE
            WHEN company_id IS NOT NULL THEN jsonb_build_object(company_id::text, property_payment_term_id)
            ELSE NULL
        END,
        ALTER COLUMN property_payment_term_id SET DEFAULT NULL
    """)

    env.cr.execute(f"""
        ALTER TABLE {table}
        ALTER COLUMN property_supplier_payment_term_id DROP DEFAULT,
        ALTER COLUMN property_supplier_payment_term_id TYPE jsonb
        USING CASE
            WHEN company_id IS NOT NULL THEN jsonb_build_object(company_id::text, property_supplier_payment_term_id)
            ELSE NULL
        END,
        ALTER COLUMN property_supplier_payment_term_id SET DEFAULT NULL
    """)
