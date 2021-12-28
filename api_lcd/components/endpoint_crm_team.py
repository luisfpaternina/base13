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
        [(["/<int:id>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, id):
        crm_team = self.env["crm.team"].search([('id','=',id)])
        if crm_team:
            res = {
                     "id": id,
                    "name": crm_team.name
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe un equipo con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True},
                "name": {"type":"string", "required": False},
                "message": {"type":"string", "required": False}
              }
        return res
