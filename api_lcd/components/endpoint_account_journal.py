from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json
import logging
logger = logging.getLogger(__name__)

class journalCard(Component):
    _inherit = 'base.rest.service'
    _name = 'account.journal.service'
    _usage = 'Account Journal'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search Account Journal
    """
    
    @restapi.method(
        [(["/<string:name>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, name):
        dict = {}
        list = []
        journal_list = []
        journal = self.env["account.journal"].name_search(name)
        journal = self.env["account.journal"].browse([i[0] for i in journal])
        if journal:
            if journal.journal_group_ids:
                for item in journal.journal_group_ids:
                    dict = {
                        "group_id": item.id,
                        "group_name": item.name
                        }
                    list.append(dict)
            res = {
                     "id": journal.id,
                    "name": journal.name,
                    "type": journal.type,
                    "journal_groups": list
                  }
        else:
            res = {
                    "message": "No existe un diario con ese nombre"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": False},
                "name": {"type":"string", "required": True},
                "type": {"type":"string", "required": False},
                "message": {"type":"string", "required": False},
                "journal_groups": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                               "group_id":{"type":"integer", "required": False},
                                               "group_name":{"type":"string", "required": False}
                                        }
                                       }
                                    }
              }
        return res
