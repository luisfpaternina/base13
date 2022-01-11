from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class ResUsers(Component):
    _inherit = 'base.rest.service'
    _name = 'res.users.service'
    _usage = 'Res User'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search res users
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
             users = self.env["res.users"].search([])
        else:
            users = self.env["res.users"].search([('name','=',name)])
        if users:
            for item in users:
                dict = {
                         "id": item.id,
                        "name": item.name,
                      }
                list.append(dict)
            res = {
                    "res_users": list
                  }
        else:
            res = {
                    "message": "No existe un usuarios con este nombre"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "res_users": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": True}
                                        }
                                       }
                                   }
              }
        return res
