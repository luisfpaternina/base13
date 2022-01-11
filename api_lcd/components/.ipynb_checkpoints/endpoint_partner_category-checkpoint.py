from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json


class PartnerCategory(Component):
    _inherit = 'base.rest.service'
    _name = 'partner.category.service'
    _usage = 'Partner Category'
    _collection = 'contact.services.private.services'
    _description = """
       API SERVICE to create search and create Partner Categories
    """
    
    @restapi.method(
        [(["/<string:name>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, name):
        list = []
        dict = {}
        if name == "all":
            category = self.env["res.partner.category"].search([])
        else:
            category = self.env["res.partner.category"].search([("name","=",name)])
        if category:
            for item in category:
                dict = {
                        "name": item.name,
                        "id": item.id,
                      }
                list.append(dict)
            res = {
                "res_partner_category": list
            }
        else:
            res = {
                "message": "no hay una categoria de cliente con este id"
            }
        return res
    
    def _validator_search(self):
        res = {
                "res_partner_category": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": True},
                                                    "message": {"type":"string", "required": False}
                                                }
                                               }
                                        }
              }
        return res
