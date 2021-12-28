from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo import fields
import json
import logging
_logger = logging.getLogger(__name__)


class ResCurrencyRate(Component):
    _inherit = 'base.rest.service'
    _name = 'res.currency.rate.service'
    _usage = 'Res Currency'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search currency rate
    """
    
    @restapi.method(
        [(["/<string:fecha>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, fecha_str):
        fecha = fields.Date.to_date(fecha_str)
        domain = [
                    ('name','=',fecha),
                    ('currency_id.id','=',2),
                    ('company_id.id','=',1)
                 ]
        res_currency = self.env["res.currency.rate"].search(domain,limit=1)
        if res_currency:
            res = {
                     "fecha": fecha,
                    "tasa": res_currency.rate
                  }
        else:
            res = {
                    "message": """No existe una tasa para esta 
                                fecha en la compañia seleccionada"""
                  }
        return res
    
    def _validator_search(self):
        res = {
                "fecha": {"type":"date", "required": True},
                "tasa": {"type":"float", "required": False},
                "message": {"type":"string", "required": False}
              }
        return res
