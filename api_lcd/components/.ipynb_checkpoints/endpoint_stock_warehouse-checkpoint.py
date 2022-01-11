from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class StockWarehouse(Component):
    _inherit = 'base.rest.service'
    _name = 'stock.warehouse.service'
    _usage = 'Stock Warehouse'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search stock warehouse
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
            stock = self.env["stock.warehouse"].search([])
        else:
            stock = self.env["stock.warehouse"].search([('name','=',name)])
        if stock:
            for item in stock:
                dict = {
                         "id": item.id,
                        "name": item.name,
                        "short_name": item.code,
                      }
                list.append(dict)
            res = {
                    "stock_warehouse": list
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe un equipo con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "stock_warehouse": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": True},
                                                    "name": {"type":"string", "required": False},
                                                    "short_name": {"type":"string", "required": False},
                                                    "message": {"type":"string", "required": False}
                                                }
                                               }
                                    }
              }
        return res
