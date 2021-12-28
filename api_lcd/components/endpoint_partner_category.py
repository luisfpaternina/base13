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
        [(["/<int:id>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, _id):
        category = self.env["res.partner.category"].browse(_id)
        if category:
            res = {
                    "name": category.name,
                    "id": _id,
                  }
        else:
            res = {
                "message": "no hay una categoria de cliente con este id"
            }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True},
                "name": {"type":"string", "required": True},
                "message": {"type":"string", "required": False},
              }
        return res
