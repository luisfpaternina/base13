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
        journal_list = []
        journal_dict = {}
        if name =="all":
            journal = self.env["account.journal"].search([])
        else:
            journal = self.env["account.journal"].name_search(name)
            journal = self.env["account.journal"].browse([i[0] for i in journal])
        if journal:
            for items in journal:
                journal_dict = {
                    "id": items.id,
                    "name": items.name,
                    "type": items.type
                    }
                journal_list.append(journal_dict)
            res = {
                     "account_journal": journal_list
                  }
        else:
            res = {
                    "message": "No existe un diario con ese nombre"
                  }
        return res
    
    def _validator_search(self):
        res = {
                "account_journal": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "name": {"type":"string", "required": True},
                                                    "type": {"type":"string", "required": False},
                                                    "message": {"type":"string", "required": False}
                                        }
                                       }
                                  }
              }
        return res
