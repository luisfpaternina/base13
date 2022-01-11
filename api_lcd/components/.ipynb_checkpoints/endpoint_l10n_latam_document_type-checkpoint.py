from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json
import logging
_logger = logging.getLogger(__name__)


class l10n_latamDocumentype(Component):
    _inherit = 'base.rest.service'
    _name = 'l10n_latam.document.type.service'
    _usage = 'Latam Document Type'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search Latam Document Type
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
            document_type = self.env["l10n_latam.document.type"].search([])
        else:
            document_type = self.env["l10n_latam.document.type"].name_search(name)
            document_type = self.env["l10n_latam.document.type"].browse([i[0] for i in document_type])
        if document_type:
            for doc in document_type:
                dict = {
                        "id": doc.id,
                        "code": doc.code,
                        "name": doc.name,
                        "doc_code_prefix": doc.doc_code_prefix,
                        "purchase_aliquots": doc.purchase_aliquots,
                        "report_name": doc.report_name,
                        "internal_type": doc.report_name,
                        "country_id": doc.country_id.id
                        }
                list.append(dict)
            res = {
                "document_type": list
                }
        else:
            res = {
                    "message": "No existe un tipo de documento con este nombre"
                    }
        return res
    
    def _validator_search(self):
        res = {
                "document_type": {"type":"list", 
                                       "schema": { 
                                        "type": "dict",
                                        "schema": {
                                                    "id": {"type":"integer", "required": False},
                                                    "code": {"type":"string", "required": False},
                                                    "name": {"type":"string", "required": False},
                                                    "message": {"type":"string", "required": False},
                                                    "doc_code_prefix": {"type":"string", "required": False},
                                                    "purchase_aliquots": {"type":"string", "required": False},
                                                    "report_name": {"type":"string", "required": False},
                                                    "internal_type": {"type":"string", "required": False},
                                                    "country_id": {"type":"integer", "required": False}
                                                }
                                               }
                            }
              }
        return res
