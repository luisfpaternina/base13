from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json
import logging
logger = logging.getLogger(__name__)

class PromotionCard(Component):
    _inherit = 'base.rest.service'
    _name = 'promotion.card.service'
    _usage = 'Promotion Card'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search and create sale order tipo entrega
    """
    
    @restapi.method(
        [(["/<int:id>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, id):
        dict = {}
        list = []
        promotion_list = []
        promotion = self.env["promotion.card"].search([('id','=',id)])
        if promotion:
            if promotion.promotion_ids:
                for item in promotion.promotion_ids:
                    dict = {
                        "sucursal_id": item.team_id.id,
                        "sucursal_name": item.team_id.name
                        }
                    list.append(dict)
            if promotion.monday:
                promotion_list.append("Monday")
            if promotion.tuesday:
                promotion_list.append("Tuesday")
            if promotion.wednesday:
                promotion_list.append("Wednesday")
            if promotion.thurday:
                promotion_list.append("Thurday")
            if promotion.friday:
                promotion_list.append("Friday")
            if promotion.saturday:
                promotion_list.append("Saturday")
            if promotion.sunday:
                promotion_list.append("Sunday")
            if promotion.all_days:
                promotion_list.append("All Days")
            res = {
                     "id": id,
                    "name": promotion.name,
                    "card_code": promotion.res_card_id.code,
                    "card": promotion.res_card_id.name,
                    "bank_code": promotion.res_bank_id.bic,
                    "bank": promotion.res_bank_id.name,
                    "start_date": promotion.start_date,
                    "end_date": promotion.end_date,
                    "percentage": promotion.percentage,
                    "promotion_days": promotion_list,
                    "sucursales": list
                  }
        else:
            res = {
                    "id": id,
                    "message": "No existe una tarjeta de promocion con este id"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True},
                "name": {"type":"string", "required": False},
                "card_code": {"type":"integer", "required": False},
                "card": {"type":"string", "required": False},
                "bank_code": {"type":"string", "required": False},
                "bank": {"type":"string", "required": False},
                "start_date": {"type":"date", "required": False},
                "end_date": {"type":"date", "required": False},
                "percentage": {"type":"float", "required": False},
                "message": {"type":"string", "required": False},
                "promotion_days": {"type":"list"},
                "sucursales": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                               "sucursal_id":{"type":"integer", "required": False},
                                               "sucursal_name":{"type":"string", "required": False}
                                        }
                                       }
                                    }
              }
        return res
