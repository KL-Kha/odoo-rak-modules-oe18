from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.http import request
from werkzeug.urls import url_parse
from odoo import Command
from markupsafe import Markup

class XMjbFieldHistoryTracking(models.Model):
	_name = "x_mjb_field_history_tracking"
	_description = "x_mjb_field_history_tracking"
	_rec_name = "x_mjb_track_model"
	_order = "id desc"

	x_mjb_is_tracking = fields.Boolean(string="Tracking?", help="This field is used to determine whether the tracking is active or not.")
	x_mjb_track_model = fields.Many2one('ir.model', string="Model", help="This field is used to determine the model to track.")
	x_mjb_track_field = fields.Many2many('ir.model.fields', 'x_mjb_track_field_rel', 'tracking_id', 'field_id', string="Fields", help="This field is used to determine the fields to track.")
	x_mjb_post_message_targer = fields.Many2many('ir.model.fields', 'x_mjb_post_message_targer_rel', 'tracking_id', 'field_id', string="Target Post Message Tracking", help="This field is used to determine the target model to post the message. If not set, the current model will be used.")
	automation_id = fields.Many2one('base.automation', string="Automated Action")
	
	display_old_date = fields.Boolean('Showing old value changed?',default=True,help="This field is used to determine whether the old value is displayed or not.")
	display_text_dynamic = fields.Text('Text incude?',help="This field is used to determine the text to include in the message post.")

	@api.onchange('x_mjb_track_model')
	def _onchange_x_mjb_track_model(self):
		self.x_mjb_track_field = [(6, 0, [])]

	def _create_update_automated_action(self):
		BaseAutomation = self.env['base.automation']
		for rec in self:
			rec.automation_id.unlink()
			if rec.x_mjb_is_tracking:
				automation_id = BaseAutomation.create({
					'name': '[MJB] Auto Log - Model: ' + rec.x_mjb_track_model.name,
					'model_id': rec.x_mjb_track_model.id,
					'trigger': 'on_create_or_write',
					'trigger_field_ids': [(6, 0, rec.x_mjb_track_field.ids)],
					'active': True,
				})

				action = self.env["ir.actions.server"].create({
					"name": "[MJB] Auto Log Tracking Actions - Model: "+ rec.x_mjb_track_model.name,
					"base_automation_id": automation_id.id,
					"state": "code",
					"code": f"""
records = records.with_context(display_old_date={rec.display_old_date},display_text_dynamic='{rec.display_text_dynamic}',x_mjb_post_message_targer={rec.x_mjb_post_message_targer.ids})
env['x_mjb_field_history_tracking']._check_update(records)                    
""",
					"model_id": rec.x_mjb_track_model.id,
				})

				automation_id.write({"action_server_ids": [Command.link(action.id)]})
				
				rec._write({
					'automation_id': automation_id.id
				})
				
	@api.model
	def create(self, vals):
		res = super(XMjbFieldHistoryTracking, self).create(vals)
		res._create_update_automated_action()
		return res

	def write(self, vals):
		res = super(XMjbFieldHistoryTracking, self).write(vals)
		self._create_update_automated_action()
		return res

	def unlink(self):
		for rec in self:
			rec.automation_id.unlink()
		return super(XMjbFieldHistoryTracking, self).unlink()

	def _check_update(self, records):
		IrModelFields = self.env['ir.model.fields']
		IrModel = self.env['ir.model']

		for record in records:
			if not self.env.context.get('old_values'):
				continue

			# Determine the automation record
			automated_id = self.env['base.automation']
			actions = record.env.context.get('__action_done')
			if actions:
				for key in actions:
					automated_id = self.env['base.automation'].browse(key.id)
					break  # Only one automation ID is needed

			old_values = self.env.context['old_values'].get(record.id, {})
			context_model = self._context.get('active_model')
			context_active_id = self._context.get('active_id')
			if not context_model or not context_active_id:
				continue

			context_record_change = self.env[context_model].browse(context_active_id)
			if not context_record_change.exists():
				continue

			# Track updated fields to avoid duplicates
			changes_list = []
			updated_fields = set()

			list_current_record = automated_id.trigger_field_ids
			model_id = IrModel.search([('model', '=', str(context_model))], limit=1)

			for field_name, old_value in old_values.items():
				field = IrModelFields.search([('model_id', '=', model_id.id), ('name', '=', field_name)], limit=1)
				if not field or field not in list_current_record:
					continue

				if field.name in updated_fields:
					continue
				updated_fields.add(field.name)

				field_type = field.ttype
				new_value = record[field_name]

				if field_type in ['many2many', 'one2many']:
					model_name = record[field_name]._name
					old_value_ids = old_value
					if isinstance(old_value, int):
						old_value_ids = self.env[model_name].browse(old_value)

					mapped_old_values = old_value_ids.mapped('display_name') or old_value_ids.mapped('name') if old_value_ids else False
					old_value = ', '.join(mapped_old_values) if mapped_old_values else ''
					mapped_new_values = (new_value.mapped('display_name') or new_value.mapped('name')) if new_value else False
					new_value = ', '.join(mapped_new_values) if mapped_new_values else ''

				elif field_type in ['many2one', 'many2one_reference']:
					old_value = old_value[1] if isinstance(old_value, tuple) else old_value
					old_value = getattr(old_value, 'display_name', getattr(old_value, 'name', old_value))
					new_value = getattr(new_value, 'display_name', getattr(new_value, 'name', new_value))

				if field_type == 'selection':
					selection_options = dict(record._fields[field.name].selection)
					old_value = selection_options.get(old_value, old_value)
					new_value = selection_options.get(new_value, new_value)

				if field_type == 'binary':
					binary_filename_field = f"{field.name}_filename"
					old_value = old_values.get(binary_filename_field, '')
					if binary_filename_field in context_record_change._fields:
						new_value = context_record_change[binary_filename_field] or ''
					else:
						new_value = ''

				display_old_value = records.env.context.get('display_old_date', True)
				change_entry = (
					f"<li>{field.field_description}: {old_value if old_value else ''} "
					f"<i class='o-mail-Message-trackingSeparator fa fa-long-arrow-right mx-1 text-600'/> {new_value if new_value else ''}</li>"
					if display_old_value else f"<li>{field.field_description}: {new_value if new_value else ''}</li>"
				)
				changes_list.append(change_entry)

			bullet_list = ""
			for item in list_current_record:
				if item.name in updated_fields:
					continue

				field_description_id = IrModelFields.search([
					('model_id', '=', model_id.id),
					('name', '=', item.name),
				], limit=1)

				if not field_description_id:
					continue

				field_label = field_description_id.field_description
				field_value = context_record_change[item.name]

				if item.ttype == 'selection':
					selection_options = dict(record._fields[item.name].selection)
					value = selection_options.get(context_record_change[item.name], context_record_change[item.name])
					bullet_list += f"<li>{field_label}: {value if value else ''}</li>"

				elif item.ttype == 'binary':
					binary_filename_field = f"{item.name}_filename"
					if binary_filename_field in context_record_change._fields:
						binary_filename_field = context_record_change[binary_filename_field] or ''
					else:
						binary_filename_field = ''
					bullet_list += f"<li>{field_label}: {binary_filename_field}</li>"

				elif item.ttype in ['one2many', 'many2many']:
					related_records = field_value
					if related_records:
						related_values = [
							rec.display_name if hasattr(rec, 'display_name') else
							rec.name if hasattr(rec, 'name') else str(rec.id)
							for rec in related_records
						]
						bullet_list += f"<li>{field_label}: {', '.join(related_values)}</li>"

				else:
					display_value = (
						field_value.display_name if hasattr(field_value, 'display_name') else
						field_value.name if hasattr(field_value, 'name') else
						field_value
					)
					bullet_list += f"<li>{field_label}: {display_value if display_value else ''}</li>"

			if changes_list:
				context = self.env.context
				try:
					main_record_id = context.get('main_record_id', False)
					if not main_record_id:
						main_record_id = context.get('active_id', False)

					base_url = request.httprequest.full_path
					model = base_url.split('call_kw/')[1].split('/')[0] if 'call_kw/' in base_url else ''
					if not model:
						model = context.get('main_model', False)
					if not model:
						model = context.get('active_model')

					post_record_id = self.env[model].browse(main_record_id)
					post_message_targer = records.env.context.get('x_mjb_post_message_targer', False)
					dynamic_text = records.env.context.get('display_text_dynamic', False)
					message_header = f"<b>{dynamic_text}</b><br>" if dynamic_text and dynamic_text != 'False' else False
					
					message_post_body = Markup(f"<ul>{''.join(changes_list)}</ul>")
					if message_header:
						message_post_body = Markup(f"{message_header}<ul>{''.join(changes_list)}</ul>")

					if post_message_targer:
						for rec in post_message_targer:
							post_record_id = self.env[context.get('active_model')].browse(context.get('active_id'))[self.env['ir.model.fields'].search([('id', '=', rec)], limit=1).name]
							post_record_id.message_post(body=message_post_body + Markup(f"<ul>{bullet_list}</ul>"))
					else:
						post_record_id.message_post(body=message_post_body + Markup(f"<ul>{bullet_list}</ul>"))
				except:
					pass