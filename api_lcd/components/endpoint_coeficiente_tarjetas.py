from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo import fields
import json
import logging
_logger = logging.getLogger(__name__)


class CoeficienteTarjetas(Component):
    _inherit = "base.rest.service"
    _name = "coeficiente.tarjetas.service"
    _usage = "Coeficiente Tarjetas"
    _collection = "contact.services.private.services"
    _description = """
         API Services to search and create sale order tipo entrega
    """
    
    #@restapi.method(
    #    [(["/<string:start_date>/<string:end_date>/<string:bank>/<string:card>/<int:quota>/search"], "GET")],
    #    output_param=restapi.CerberusValidator("_validator_search"),
    #    auth="public",
    #)
    
    def search(self,start_date,end_date,bank,card,quota):
        start = fields.Date.to_date(start_date)
        end = fields.Date.to_date(end_date)
        _logger.info("tipo quota***************")
        _logger.info(bank)
        _logger.info(card)
        _logger.info(quota)
        _logger.info(start)
        _logger.info(end)
        domain = [
            ("start_date","=",start),
            ("end_date","=",end),
            ("bank_id.name","=",bank),
            ("card_id.name","=",card),
            ("quota","=",int(quota))
        ]
        _logger.info(domain)
        coeficiente_tarjetas = self.env["coeficiente.tarjetas"].search(domain)
        if coeficiente_tarjetas:
            res = {
                     "id": id,
                    "start_date": coeficiente_tarjetas.start_date,
                    "end_date": coeficiente_tarjetas.end_date,
                    "bank_code": coeficiente_tarjetas.bank_id.bic,
                    "bank": coeficiente_tarjetas.bank_id.name,
                    "card_code": coeficiente_tarjetas.card_id.code,
                    "card": coeficiente_tarjetas.card_id.name,
                    "quota": coeficiente_tarjetas.quota,
                    "rate": coeficiente_tarjetas.rate
                  }
        else:
            res = {
                    "message": "No existe un coeficiente de tarjeta con esos datos"
                  }
        return  res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": False},
                "start_date": {"type":"string", "required": True},
                "end_date": {"type":"string", "required": True},
                "bank_code": {"type":"string", "required": False},
                "bank": {"type":"string", "required": True},
                "card_code": {"type":"integer", "required": False},
                "card": {"type":"string", "required": True},
                "message": {"type":"string", "required": False},
                "quota": {"type":"string", "required": True},
                "rate": {"type":"float", "required": False},
              }
        return res
