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
        invoice._reverse_moves()
        reversal = self.env["account.move"].search([("reversed_entry_id","=",invoice.id)], limit=1, order='create_date desc')
        res["message"] = "se creo el la factura rectificativa: {reserve}"\
                .format(reserve = reversal.name)
        return res

    def _validator_create(self):
        res = {
                "name": {"type":"string", "required": True}
              }
        return res
