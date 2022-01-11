from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class ResTarjeta(Component):
    _inherit = 'base.rest.service'
    _name = 'res.tarjeta.service'
    _usage = 'Res Tarjeta'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search res tarjeta
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
             tarjeta = self.env["res.tarjeta"].search([])
        else:
            tarjeta = self.env["res.tarjeta"].search([('name','=',name)])
        if tarjeta:
            for item in tarjeta:
                dict = {
                         "id": item.id,
                        "name": item.name,
                        "code": item.code,
                        "shopin": item.shopin or "",
                        "codglamit": item.codglamit or "",
                        "type": item.type,
                      }
                list.append(dict)
            res = {
                    "res_tarjeta": list
                  }
        else:
            res = {
                    "message": "No existe un usuarios con este nombre"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "res_tarjeta": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": False},
                                                    "code": {"type":"integer", "required": False},
                                                    "shopin": {"type":"string", "required": False},
                                                    "codglamit": {"type":"string", "required": False},
                                                    "type": {"type":"string", "required": False}
                                                }
                                               }
                                   }
              }
        return res
