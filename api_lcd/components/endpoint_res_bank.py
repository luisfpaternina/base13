from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class ResBank(Component):
    _inherit = 'base.rest.service'
    _name = 'res.bank.service'
    _usage = 'Res Bank'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search res bank
    """
    
    @restapi.method(
        [(["/<int:id>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, id):
        bank = self.env["res.bank"].search([('id','=',id)])
        if bank:
            res = {
                     "id": id,
                    "name": bank.name,
                    "bic": bank.bic,
                    "country_id": bank.country.id,
                    "country": bank.country.name
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe un Banco con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True},
                "name": {"type":"string", "required": False},
                "bic": {"type":"string", "required": False},
                "country_id": {"type":"integer", "required": False},
                "country": {"type":"string", "required": False},
                "message": {"type":"string", "required": False},
              }
        return res
