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
        [(["/<string:name>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, name):
        dict = {}
        list = []
        if name == "all":
            bank = self.env["res.bank"].search([])
        else:
            bank = self.env["res.bank"].search([('name','=',name)])
        if bank:
            for item in bank:
                dict = {
                         "id": item.id,
                        "name": item.name,
                        "bic": item.bic,
                        "country_id": item.country.id
                      }
                list.append(dict)
            res = {
                "res_bank": list
            }
        else:
            res = {
                    "id": id,
                    "message": "No existe un Banco con este nombre"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "res_bank": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": False},
                                                    "bic": {"type":"string", "required": False},
                                                    "country_id": {"type":"integer", "required": False},
                                                    "message": {"type":"string", "required": False}
                                                }
                                               }
                            }
              }
        return res
