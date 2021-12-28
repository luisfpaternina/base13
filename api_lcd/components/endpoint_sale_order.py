from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo import fields
import json


class SaleOrder(Component):
    _inherit = 'base.rest.service'
    _name = 'sale.order.service'
    _usage = 'Sale Order'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search and create Sale Order
    """
    
    @restapi.method(
        [(["/<string:name>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, name):
        sale = self.env["sale.order"].search([('name','=',name)])
        if sale:
            res = {
                    "name": sale.name,
                    "state": sale.state
                  }
        else:
            res = {
                    "message": "No existe una sale order con ese nombre"
                  }
        return res
    
    def create(self, **params):
        fecha = fields.Date.to_date(params["fecha_cierta"])
        dict = {}
        res = {
                "partner_id": params["partner_id"],
                "canal_venta_id": params["canal_venta_id"],
                "tipo_entrega_id": params["tipo_entrega_id"],
                "zona_id": params["zona_id"],
                "pricelist_id": params["pricelist_id"],
                "invoice_policy": params["invoice_policy"],
                "fecha_cierta": fecha
              }
        sale = self.env['sale.order'].create(res)
        if params["order_lines"]:
            for item in params["order_lines"]:
                sale.write({"order_line": [(0,0,item)]})
        sale.action_confirm()
        sale._create_invoices()
        invoice = self.env["account.move"].search([("invoice_origin","=",sale.name)],limit=1)
        invoice.write({"journal_id": params["journal_id"]})
        invoice.action_post()
        res["message"] = "se creo la Factura: {sale}"\
                .format(sale = invoice.name)
        return res
    
    def _validator_search(self):
        res = {
                "state": {"type":"string", "required": True},
                "name": {"type":"string", "required": False},
                "message": {"type":"string", "required": False}
              }
        return res

    def _validator_create(self):
        res = {
                "partner_id": {"type":"integer", "required": True},
                "canal_venta_id": {"type":"integer", "required": False},
                "message": {"type":"string", "required": False},
                "tipo_entrega_id": {"type":"integer", "required": False},
                "zona_id": {"type":"integer", "required": False},
                "pricelist_id": {"type":"integer", "required": False},
                "invoice_policy": {"type":"string", "required": False},
                "fecha_cierta": {"type":"string", "required": False},
                "journal_id": {"type":"integer", "required": False},
                "order_lines": {"type":"list",
                                "schema": {"type": "dict",
                                        "schema": {
                                            "product_id": {"type":"integer", "required": False},
                                            "product_uom_qty": {"type":"float", "required": False},
                                             "entrega_tienda": {"type":"string", "required": True}
                                                  }
                                          }
                               }
              }
        return res
