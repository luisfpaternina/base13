from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo import fields
import json
import logging
_logger = logging.getLogger(__name__)


class ProductPricelist(Component):
    _inherit = 'base.rest.service'
    _name = 'product.pricelist.service'
    _usage = 'Pricelist'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search Product Pricelist
    """
    
    @restapi.method(
        [(["/<string:name>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, name):
        list = []
        dict = {}
        pricelist = self.env["product.pricelist"].name_search(name)
        pricelist = self.env["product.pricelist"].browse([i[0] for i in pricelist])
        if pricelist:
            for doc in pricelist:
                res = {
                        "id": doc.id,
                        "name": doc.name,
                    }
                day = fields.Date.today()
                for item in doc.item_ids:
                    if item.date_start <= day <= item.date_end:
                        if item.base_pricelist_id:
                            for items in item.base_pricelist_id.item_ids:
                                price = items.fixed_price
                                price_discount = 0
                                price_surcharge = 0
                                if item.product_tmpl_id.id == items.product_tmpl_id.id:
                                    price_discount = item.price_discount
                                    price_surcharge = item.price_surcharge
                                    price = items.fixed_price - (items.fixed_price * (price_discount/100)) + price_surcharge
                                dict = {
                                    "product_id": items.product_tmpl_id.id,
                                    "product_name": items.product_tmpl_id.name,
                                    "price_fix": price,
                                    "price": items.fixed_price,
                                    "price_discount": price_discount,
                                    "price_surcharge": price_surcharge
                                    }
                                list.append(dict)
                        else:
                            dict = {
                                    "product_id": item.product_tmpl_id.id,
                                    "product_name": item.product_tmpl_id.name,
                                    "price": item.fixed_price
                                    }
                            list.append(dict)
                        res["products"] = list
                            
                            
        else:
            res = {
                    "message": "No existe un tipo de documento con este nombre"
                    }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": False},
                "name": {"type":"string", "required": False},
                "message": {"type":"string", "required": False},
                 "products": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                               "product_id":{"type":"integer", "required": False},
                                               "product_name":{"type":"string", "required": False},
                                               "price":{"type":"float", "required": False},
                                               "price_fix":{"type":"float", "required": False},
                                               "price_discount":{"type":"float", "required": False},
                                               "price_surcharge":{"type":"float", "required": False}
                                        }
                                       }
                                    }
              }
        return res
