from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('cluedoo')
class TestEmployeePrivateAddress(TransactionCase):
    def test_create_employee(self):
        self.employee = self.env['hr.employee'].create({
            'name': 'Private Employee',
        })

        self.assertEqual(self.employee.address_home_id.type, 'private')
