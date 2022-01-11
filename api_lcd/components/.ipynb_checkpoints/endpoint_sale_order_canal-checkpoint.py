from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class SaleOrderCanal(Component):
    _inherit = 'base.rest.service'
    _name = 'sale.order.canal.service'
    _usage = 'Sale Order Canal'
    _collection = 'contact.services.private.services'
    _description = """
        API Services to search and create sale order canal
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
             canal = self.env["sale.order.canal"].search([])
        else:
            canal = self.env["sale.order.canal"].search([('name','=',name)])
        if canal:
            for item in canal:
                dict = {
                        "id": item.id,
                        "name": item.name,
                        "codigo": item.codigo,
                        "dias_maximos": item.dias_maximos,
                      }
                list.append(dict)
            res = {
                    "sale_order_canal": list
                  }
        else:
            res = {
                    "message": "No existe un canal con este nombre"
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
                                                    "dias_maximos": {"type":"integer", "required": False},
                                                    "message": {"type":"string", "required": False},
                                                }
                                               }
                             }
              }
        return res
