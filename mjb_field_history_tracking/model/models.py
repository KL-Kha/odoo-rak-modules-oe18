# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class Base(models.AbstractModel):
    _inherit = 'base'
    
    def web_save(self, vals, specification: dict[str, dict], next_id=None) -> list[dict]:
        self = self.with_context(main_record_id=self.ids,main_model=self._name)
        return super(Base,self).web_save(vals, specification, next_id)