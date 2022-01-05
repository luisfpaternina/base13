from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo import fields
import json
import logging
_logger = logging.getLogger(__name__)


class AccountMoveReversal(Component):
    _inherit = 'base.rest.service'
    _name = 'account.move.reversal.service'
    _usage = 'Account Move Reversal'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to create Account Move Reversal
    """
    
    def create(self, **params):
        res = {"name": params["name"]}
        invoice = self.env["account.move"].search([("name","=",params["name"])])
        reversal = self.env["account.move.reversal"].create({
            "refund_method": params["refund_method"],
            "reason": params["reason"],
            "journal_id": params["journal_id"],
            "move_id": invoice.id,
        })
        reversal.reverse_moves()
        invoice_reversal = self.env["account.move"].search([("reversed_entry_id","=",invoice.id)],limit=1)
        for line in invoice_reversal.invoice_line_ids.with_context(check_move_validity=False):
            quantity = line.quantity
            line.discount = params["discount"]
            line.quantity = quantity
            line._onchange_balance()
            line.move_id._onchange_invoice_line_ids()
            line._onchange_mark_recompute_taxes()
        invoice_reversal.action_post()
        res["message"] = "se creo el la factura rectificativa: {reserve}"\
                .format(reserve = invoice_reversal.name)
        return res

    def _validator_create(self):
        res = {
                "name": {"type":"string", "required": True},
                "refund_method": {"type":"string", "required": True},
                "reason": {"type":"string", "required": True},
                "journal_id": {"type":"integer", "required": False},
                "discount": {"type":"float", "required": False}
              }
        return res
