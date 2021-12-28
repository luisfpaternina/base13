from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json
import logging
logger = logging.getLogger(__name__)

class SaleOrderZona(Component):
    _inherit = 'base.rest.service'
    _name = 'sale.order.zona.service'
    _usage = 'Sale Order Zona'
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
        dict = {}
        list = []
        zona = self.env["sale.order.zona"].search([('id','=',id)])
        if zona:
            if zona.codigos_postales:
                for item in zona.codigos_postales:
                    dict = {
                        "name": item.name,
                        "zona_id": item.zona_id.id,
                        "zona_name": item.zona_id.name
                        }
                    list.append(dict)
            res = {
                     "id": id,
                    "name": zona.name,
                    "codigos_postales": list
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe una zona con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True},
                "name": {"type":"string", "required": False},
                "codigo": {"type":"string", "required": False},
                "message": {"type":"string", "required": False},
                "codigos_postales": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                               "name":{"type":"string", "required": False},
                                               "zona_id":{"type":"integer", "required": False},
                                               "zona_name":{"type":"string", "required": False}
                                        }
                                       }
                                    }
              }
        return res
