from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json
import logging
logger = logging.getLogger(__name__)

class ProductProduct(Component):
    _inherit = 'base.rest.service'
    _name = 'product.product.service'
    _usage = 'Products'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search products
    """
    
    @restapi.method(
        [(["/<string:default_code>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, default_code):
        dict = {}
        list = []
        att_dict = {}
        att_list = []
        tax_list = []
        tax_dict = {}
        sale = "False"
        product = self.env["product.product"].search([('default_code','=',default_code)])
        if product:
            if product.sale_ok:
                sale = "True"
            if product.taxes_id:
                for tax in product.taxes_id:
                    tax_dict = {
                        "tax_id": tax.id,
                        "tax_name": tax.name
                    }
                    tax_list.append(tax_dict)
            if product.product_template_attribute_value_ids:
                for attribute in product.product_template_attribute_value_ids:
                    att_dict = {
                        "attribute_id": attribute.attribute_id.id,
                        "attribute_name": attribute.attribute_id.name,
                        "attribute_value_id": attribute.product_attribute_value_id.id,
                        "attribute_value_name": attribute.product_attribute_value_id.name
                    }
                    att_list.append(att_dict)
            kit = self.env['mrp.bom'].search([('product_id','=',product.id),("active","=",True)])
            if kit:
                for item in kit.bom_line_ids:
                    sale = "False"
                    if item.product_id.sale_ok:
                        sale = "True"
                    dict = {
                        "product_id": item.product_id.id,
                        "product_name": item.product_id.name,
                        "sale_ok": sale
                        }
                    list.append(dict)
            res = {
                     "id": product.id,
                    "sale_ok": sale,
                    "type": product.type,
                    "default_code": product.default_code,
                    "name": product.name,
                    "barcode": product.barcode or "",
                    "description": product.description_sale or "",
                    "product_category": [product.categ_id.id,product.categ_id.name],
                    "arba_code": product.arba_code or "",
                    "taxes": tax_list,
                    "standard_price": product.standard_price,
                    "unit_measure": [product.uom_id.id,product.uom_id.name],
                    "attributes": att_list,
                    "list_type": kit.type or "",
                    "reference": kit.code or "",
                    "components": list
                  }
        else:
            res = {
                    "message": "No existe una producto con este referencia"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": False},
                "name": {"type":"string", "required": False},
                "default_code": {"type":"string", "required": False},
                "sale_ok": {"type":"string", "required": False},
                "message": {"type":"string", "required": False},
                "barcode": {"type":"string", "required": False},
                "description": {"type":"string", "required": False},
                "product_category": {"type":"list", "required": False},
                "arba_code": {"type":"string", "required": False},
                "standard_price": {"type":"float", "required": False},
                "unit_measure": {"type":"list", "required": False},
                "list_type": {"type":"string", "required": False},
                "reference": {"type":"string", "required": False},
                "taxes": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                               "tax_id":{"type":"integer", "required": False},
                                               "tax_name":{"type":"string", "required": False}
                                        }
                                       }
                                    },
                "attributes": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                               "attribute_id":{"type":"integer", "required": False},
                                               "attribute_name":{"type":"string", "required": False},
                                               "attribute_value_id":{"type":"integer", "required": False},
                                               "attribute_value_name":{"type":"string", "required": False}
                                        }
                                       }
                                    },
                "components": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                               "product_id":{"type":"integer", "required": False},
                                               "product_name":{"type":"string", "required": False},
                                               "sale_ok":{"type":"string", "required": False}
                                        }
                                       }
                                    }
              }
        return res
