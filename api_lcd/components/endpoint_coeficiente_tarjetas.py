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
         API Services to search coeficiente de tarjetas
    """
    
    
    def create(self,**params):
        domain = [
            ("start_date","=",params["start_date"]),
            ("end_date","=",params["end_date"]),
            ("bank_id","=",params["bank"]),
            ("card_id","=",params["card"]),
            ("quota","=",params["quota"])
        ]
        coeficiente_tarjetas = self.env["coeficiente.tarjetas"].search(domain)
        if coeficiente_tarjetas:
            res = {
                    "start_date": coeficiente_tarjetas.start_date,
                    "end_date": coeficiente_tarjetas.end_date,
                    "bank_code": coeficiente_tarjetas.bank_id.bic,
                    "bank": coeficiente_tarjetas.bank_id.id,
                    "card_code": coeficiente_tarjetas.card_id.code,
                    "card": coeficiente_tarjetas.card_id.id,
                    "quota": coeficiente_tarjetas.quota,
                    "rate": coeficiente_tarjetas.rate
                  }
        else:
            res = {
                    "message": "No existe un coeficiente de tarjeta con esos datos"
                  }
        return  res
    
    def _validator_create(self):
        res = {
                "id": {"type":"integer", "required": False},
                "start_date": {"type":"string", "required": True},
                "end_date": {"type":"string", "required": True},
                "bank_code": {"type":"string", "required": False},
                "bank": {"type":"integer", "required": False},
                "card_code": {"type":"integer", "required": False},
                "card": {"type":"integer", "required": False},
                "message": {"type":"string", "required": False},
                "quota": {"type":"integer", "required": False},
                "rate": {"type":"float", "required": False},
              }
        return res
