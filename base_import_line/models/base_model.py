# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, _
# from odoo.exceptions import Warning
from werkzeug.exceptions import BadRequest

class BaseModel(models.AbstractModel):
    _inherit = 'base'

    def all_btn_import_line(self):
        self.ensure_one()
        ctx = self._context.copy()
        field_name = ctx.get('o2m_field')
        if not field_name:
            raise Warning(_('The field of lines is not found !'))
        args = [('model', '=', self._name),
                ('name', '=', field_name)]
        o2m_field = self.env['ir.model.fields'].sudo().search(args, limit=1)
        if not o2m_field:
            raise Warning(_('The field of lines does not correct !'))
        if o2m_field.ttype != 'one2many':
            raise Warning(_('Type of field is not a one2many !'))
        ctx.update({
            'relation_field': o2m_field.relation_field,
            'relation_field_value': self.id
        })
        res = {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {
                'model': o2m_field.relation,
                'context': ctx,
            }
        }
        return res

    @api.model
    def create(self, vals):
        ctx = self._context
        if ctx.get('relation_field') and ctx.get('relation_field_value') and \
                ctx.get('import_file'):
            vals.update({ctx['relation_field']: ctx['relation_field_value']})
        res = super(BaseModel, self).create(vals)
        return res