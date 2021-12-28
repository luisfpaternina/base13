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
        [(["/<int:id>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, id):
        afip = self.env["l10n_ar.afip.responsibility.type"].search([('id','=',id)])
        if afip:
            res = {
                     "id": id,
                    "name": afip.name,
                    "code": afip.code
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
                "message": {"type":"string", "required": False},
                "code": {"type":"string", "required": False}
              }
        return res
