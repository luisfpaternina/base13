from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class SaleOrderTipoEntrega(Component):
    _inherit = 'base.rest.service'
    _name = 'sale.order.tipo_entrega.service'
    _usage = 'Sale Order Tipo Entrega'
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
        tipo_entrega = self.env["sale.order.tipo_entrega"].search([('id','=',id)])
        if tipo_entrega:
            res = {
                     "id": id,
                    "name": tipo_entrega.name,
                    "codigo": tipo_entrega.codigo,
                    "tiempo_entrega": tipo_entrega.tiempo_entrega,
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe un tipo de entrega con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True},
                "name": {"type":"string", "required": False},
                "codigo": {"type":"string", "required": False},
                "tiempo_entrega": {"type":"integer", "required": False},
                "message": {"type":"string", "required": False},
              }
        return res
