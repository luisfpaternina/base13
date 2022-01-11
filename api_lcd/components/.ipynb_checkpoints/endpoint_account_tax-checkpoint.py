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
        [(["/<string:name>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, name):
        dict = {}
        list = []
        if name == "all":
             tax = self.env["account.tax"].search([])
        else:
            tax = self.env["account.tax"].search([('name','=',name)])
        if tax:
            for item in tax:
                dict = {
                         "id": item.id,
                        "name": item.name,
                        "type_tax": item.type_tax_use,
                        "amount": item.amount
                      }
                list.append(dict)
            res = {
                    "account_tax": list
                  }
        else:
            res = {
                    "message": "No existe un impuesto con este nombre"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "account_tax": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": True},
                                                    "type_tax": {"type":"string", "required": False},
                                                    "amount": {"type":"float", "required": False},
                                                    "message": {"type":"string", "required": False},
                                        }
                                       }
                                   }
              }
        return res
