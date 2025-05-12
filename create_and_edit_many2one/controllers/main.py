from odoo import http
from odoo.http import request

class create_and_edit_many2one(http.Controller):
    @http.route('/web/create_and_edit_many2one/check_permission', type='json', auth="user")
    def check_permission(self):
        user = request.env.user
        return user.has_group('create_and_edit_many2one.group_allo_create_edit_many2one')
