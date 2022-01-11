from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo import fields
import json
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(Component):
    _inherit = 'base.rest.service'
    _name = 'sale.order.service'
    _usage = 'Sale Order'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search and create Sale Order
    """
    
    #@restapi.method(
    #    [(["/<string:name>/search"], "GET")],
    #    output_param=restapi.CerberusValidator("_validator_search"),
    #    auth="public",
    #)
    
    def search(self, name):
        list = []
        dict = {}
        sale = self.env["account.move"].search([('name','=',name)])
        if sale:
            stock = self.env["stock.picking"].search([("origin","=",sale.invoice_origin)],limit=1)
            for item in stock.move_line_ids_without_package:
                dict = {
                    "product_id": item.product_id.id,
                    "product_name": item.product_id.name,
                    "product_uom_qty": item.product_uom_qty
                }
                list.append(dict)
            res = {
                    "name": sale.name,
                    "state": sale.state,
                    "invoice_payment_state": sale.invoice_payment_state,
                    "stock_name": stock.name,
                    "move_line_ids_without_package": list,
                  }
            
        else:
            res = {
                    "message": "No existe una Factura con ese nombre"
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
                "user_id": params["user_id"],
                "team_id": params["team_id"],
                "warehouse_id": params["warehouse_id"],
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
        stock = self.env["stock.picking"].search([("origin","=",sale.name)],limit=1)
        stock.action_assign()
        for item in params["order_lines"]:
            for value in stock.move_ids_without_package:
                if value.product_id.id == item["product_id"] and item["entrega_tienda"] == "SI":
                    value.write({"quantity_done": item["product_uom_qty"]})
        stock.button_validate()
        res["message"] = "se creo la Factura: {sale}"\
                .format(sale = invoice.name)
        return res
    
    def _validator_search(self):
        res = {
                "state": {"type":"string", "required": False},
                "name": {"type":"string", "required": True},
                "message": {"type":"string", "required": False},
                "stock_name": {"type":"string", "required": False},
                "invoice_payment_state": {"type":"string", "required": False},
                "move_line_ids_without_package": {"type":"list",
                                "schema": {"type": "dict",
                                        "schema": {
                                            "product_id": {"type":"integer", "required": False},
                                            "product_name": {"type":"string", "required": False},
                                            "product_uom_qty": {"type":"float", "required": False}
                                                  }
                                          }
                               }
              }
        return res

    def _validator_create(self):
        res = {
                "partner_id": {"type":"integer", "required": True},
                "canal_venta_id": {"type":"integer", "required": False},
                "message": {"type":"string", "required": False},
                "tipo_entrega_id": {"type":"integer", "required": False},
                "zona_id": {"type":"integer", "required": False},
                "user_id": {"type":"integer", "required": False},
                "team_id": {"type":"integer", "required": False},
                "warehouse_id": {"type":"integer", "required": False},
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
