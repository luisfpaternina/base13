from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class CrmTeam(Component):
    _inherit = 'base.rest.service'
    _name = 'crm.team.service'
    _usage = 'CRM Team'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search and create sale order tipo entrega
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
            crm_team = self.env["crm.team"].search([])
        else:
            crm_team = self.env["crm.team"].search([('name','=',name)])
        if crm_team:
            for item in crm_team:
                dict = {
                         "id": item.id,
                        "name": item.name
                      }
                list.append(dict)
            res = {
                "crm_team": list
            }
        else:
            res = {
                    "message": "No existe un equipo con este nombre"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "crm_team": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": True},
                                                    "message": {"type":"string", "required": False}
                                                  }
                                       }
                               }
            }
        return res
