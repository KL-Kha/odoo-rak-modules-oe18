from odoo import http
from odoo.http import request

class mjb_create_and_edit_many2one(http.Controller):
    @http.route('/web/mjb_create_and_edit_many2one/check_permission', type='json', auth="user")
    def check_permission(self):
        user = request.env.user
        return user.has_group('mjb_create_and_edit_many2one.group_allo_create_edit_many2one')
