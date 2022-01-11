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
        [(["/<string:name>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, name):
        dict = {}
        list = []
        if name == "all":
             tipo_entrega = self.env["sale.order.tipo_entrega"].search([])
        else:
            tipo_entrega = self.env["sale.order.tipo_entrega"].search([('name','=',name)])
        if tipo_entrega:
            for item in tipo_entrega:
                dict = {
                         "id": item.id,
                        "name": item.name,
                        "codigo": item.codigo,
                        "tiempo_entrega": item.tiempo_entrega,
                      }
                list.append(dict)
            res = {
                    "tipo_entrega": list
                  }
        else:
            res = {
                    "message": "No existe un tipo de entrega con este nombre"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "tipo_entrega": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": False},
                                                    "codigo": {"type":"string", "required": False},
                                                    "tiempo_entrega": {"type":"integer", "required": False},
                                                    "message": {"type":"string", "required": False},
                                                }
                                               }
                                    }
              }
        return res
