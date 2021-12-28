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
        [(["/<int:id>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, id):
        stock = self.env["stock.warehouse"].search([('id','=',id)])
        if stock:
            res = {
                     "id": id,
                    "name": stock.name,
                    "short_name": stock.code,
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
                "short_name": {"type":"string", "required": False},
                "message": {"type":"string", "required": False}
              }
        return res
