from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo import fields
import json
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(Component):
    _inherit = 'base.rest.service'
    _name = 'account.payment.group.service'
    _usage = 'Account Payment'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to create Account Payment
    """
    
    def create(self, **params):
        res = {"name": params["name"]}
        invoice = self.env["account.move"].search([("name","=",params["name"])])
        payment = self.env["account.payment.group"].create({
            'partner_type': 'customer',
            'partner_id': invoice.partner_id.id,
            'payment_date': fields.Date.today(),
            'communication': invoice.name,
        })
        new_payment = self.env['account.payment'].\
        with_context(active_ids=invoice.ids, active_model='account.move', active_id=invoice.id)
        new_payment.create({
            'payment_type': 'inbound',
            'has_invoices': True,
            'payment_method_id': 1,
            'partner_type': 'customer',
            'partner_id': invoice.partner_id.id,
            'amount': params["amount"],
            'payment_date': fields.Date.today(),
            'journal_id': params["journal_id"],
            'communication': invoice.name,
            'payment_group_id': payment.id
        })
        domain = [("move_id","=",invoice.id)]
        payment.to_pay_move_line_ids = self.env['account.move.line'].search(domain)
        #payment.post()
        res["message"] = "se creo el Pago: {pay}"\
                .format(pay = payment.name)
        return res

    def _validator_create(self):
        res = {
                "name": {"type":"string", "required": True},
                "journal_id": {"type":"integer", "required": False},
                "amount": {"type":"float", "required": False}
              }
        return res
