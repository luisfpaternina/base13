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
         API Services to search sale order zona
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
            zona = self.env["sale.order.zona"].search([])
        else:
            zona = self.env["sale.order.zona"].search([('name','=',name)])
        if zona:
            for item in zona:
                dict = {
                         "id": item.id,
                        "name": item.name
                      }
                list.append(dict)
            res = {
                    "sale_order_canal": list
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe una zona con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "sale_order_canal": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": False},
                                                    "codigo": {"type":"string", "required": False},
                                                    "message": {"type":"string", "required": False},
                                        }
                                       }
                                }
              }
        return res
