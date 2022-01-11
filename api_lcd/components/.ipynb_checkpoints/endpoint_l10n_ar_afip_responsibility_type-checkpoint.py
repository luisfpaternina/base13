from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class l10n_arAfipResponsibilityType(Component):
    _inherit = 'base.rest.service'
    _name = 'l10n_ar.afip.responsibility.type.service'
    _usage = 'l10n_ar Afip Responsibility Type'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search Afip Responsibility Type
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
            afip = self.env["l10n_ar.afip.responsibility.type"].search([])
        else:
            afip = self.env["l10n_ar.afip.responsibility.type"].search([('name','=',name)])
        if afip:
            for item in afip:
                dict = {
                     "id": item.id,
                    "name": item.name,
                    "code": item.code
                      }
                list.append(dict)
            res = {
                "afip_responsibility": list
                }
        else:
            res = {
                    "id": id,
                    "message": "No existe un equipo con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "afip_responsibility": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": True},
                                                    "message": {"type":"string", "required": False},
                                                    "code": {"type":"string", "required": False}
                                                }
                                               }
                            }
              }
        return res
