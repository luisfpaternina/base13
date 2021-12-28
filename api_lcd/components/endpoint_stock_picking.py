from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json
import logging
_logger = logging.getLogger(__name__)


class StockPicking(Component):
    _inherit = 'base.rest.service'
    _name = 'stock.picking.service'
    _usage = 'Stock Picking'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search Stock Picking
    """
    
    #@restapi.method(
    #    [(["/<string:name>/search"], "GET")],
    #    output_param=restapi.CerberusValidator("_validator_search"),
    #    auth="public",
    #)
    
    def search(self, name):
        dict = {}
        list = []
        _logger.info(name)
        _logger.info(type(name))
        stock_picking = self.env["stock.picking"].name_search(name)
        stock_picking = self.env["stock.picking"].browse([i[0] for i in stock_picking])
        if stock_picking:
            for pick in stock_picking:
                if pick.move_ids_without_package:
                    for item in pick.move_ids_without_package:
                        dict = {
                            "product_id": item.product_id.id,
                            "product_name": item.product_id.name,
                            "quantity_done": item.quantity_done
                        }
                        list.append(dict)
                res = {
                        "id": pick.id,
                        "state": pick.state,
                        "origin": pick.origin,
                        "name": name,
                        "partner_id": pick.partner_id.id,
                        "partner_name": pick.partner_id.name,
                        "picking_type_id": pick.picking_type_id.id,
                        "picking_type_name": pick.picking_type_id.name,
                        "scheduled_date": pick.scheduled_date,
                        "date_done": pick.date_done,
                        "owner_id": pick.owner_id.id,
                        "owner_name": pick.owner_id.name,
                        "move_ids_without_package": list
                        }
        else:
            res = {
                    "message": "No existe una trasferencia con este nombre"
                    }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": False},
                "state": {"type":"string", "required": False},
                "origin": {"type":"string", "required": False},
                "name": {"type":"string", "required": True},
                "message": {"type":"string", "required": False},
                "partner_id": {"type":"integer", "required": False},
                "partner_name": {"type":"string", "required": False},
                "picking_type_id": {"type":"integer", "required": False},
                "picking_type_name": {"type":"string", "required": False},
                "scheduled_date": {"type":"string", "required": False},
                "date_done": {"type":"string", "required": False},
                "owner_id": {"type":"integer", "required": False},
                "owner_name": {"type":"string", "required": False},
                 "move_ids_without_package": {"type":"list", "required": False,
                              "schema": {"type": "dict","required": False,
                                        "schema": {
                                            "product_id": {"type":"integer", "required": False},
                                            "product_name": {"type":"string", "required": False},
                                            "quantity_done": {"type":"float", "required": False}
                                        }
                                }
                             }
              }
        return res
