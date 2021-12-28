from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class AccountTax(Component):
    _inherit = 'base.rest.service'
    _name = 'account.tax.service'
    _usage = 'Account Tax'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search account tax
    """
    
    @restapi.method(
        [(["/<int:id>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, id):
        tax = self.env["account.tax"].search([('id','=',id)])
        if tax:
            res = {
                     "id": id,
                    "name": tax.name,
                    "type_tax": tax.type_tax_use,
                    "amount": tax.amount
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe un impuesto con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True},
                "name": {"type":"string", "required": False},
                "type_tax": {"type":"string", "required": False},
                "amount": {"type":"float", "required": False},
                "message": {"type":"string", "required": False},
              }
        return res
