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
        [(["/<int:id>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, id):
        canal = self.env["sale.order.canal"].search([('id','=',id)])
        if canal:
            res = {
                     "id": id,
                    "name": canal.name,
                    "codigo": canal.codigo,
                    "dias_maximos": canal.dias_maximos,
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe un canal con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True},
                "name": {"type":"string", "required": False},
                "codigo": {"type":"string", "required": False},
                "dias_maximos": {"type":"integer", "required": False},
                "message": {"type":"string", "required": False},
              }
        return res
