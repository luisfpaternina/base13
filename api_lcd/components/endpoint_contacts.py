import logging
import json
from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
from odoo import fields
_logger = logging.getLogger(__name__)


class Contacts(Component):
    _inherit = 'base.rest.service'
    _name = 'contact.service'
    _usage = 'Contacts'
    _collection = "contact.services.private.services"
    _description = """
         New API Services to search and create Contacts
    """
    
    @restapi.method(
        [(["/<string:vat>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, vat):
        person = self.env["res.partner"].search([('vat','=',vat)])
        dict_categ = {}
        list_categ = []
        dict_taxes = {}
        list_taxes = []
        if person.category_id:
            for categ in person.category_id:
                dict_categ = {
                    "id": categ.id,
                    "name": categ.name
                }
                list_categ.append(dict_categ)
        if person.impuestos_padron:
            for tax in person.impuestos_padron:
                dict_taxes = {
                    "id": tax.id,
                    "name": tax.name
                }
                list_taxes.append(dict_taxes)
        res = {
                "id": person.id,
                "name": person.name,
                "l10n_latam_identification_type_id": person.
                l10n_latam_identification_type_id.id,
                "vat": vat,
                "l10n_ar_afip_responsibility_type_id": person.
                l10n_ar_afip_responsibility_type_id.id or 0,
                "company_type": person.company_type,
                "ref": person.ref or '',
                "phone": person.phone or '',
                "mobile": person.mobile or '',
                "email": person.email or '',
                "direccion": person.street or '',
                "direccion_1": person.street2 or '',
                "casa": person.street_number or '',
                "puerta": person.street_number2 or '',
                "city": person.city or '',
                "state_id": person.state_id.id or 0,
                "zip": person.zip or '',
                "country_id": person.country_id.id or 0,
                "etiquetas": list_categ,
                "comercial": person.user_id.id or '',
                "equipo_venta": person.team_id.id or 0,
                "tarifa_contacto": person.property_product_pricelist.id or 0,
                "canal_venta": person.canal_venta_id.id or 0,
                "tipo_entrega":  person.tipo_entrega_id.id or 0,
                "zona": person.zona_id.id or 0,
                "estado_afip": person.estado_padron or '',
                "ganancias": person.imp_ganancias_padron or '',
                "regimen_ganancias": person.default_regimen_ganancias_id.id or 0,
                "responsabilidad_iva": person.imp_iva_padron or 0,
                "integrante_sociedad": person.integrante_soc_padron or '',
                "monotributo": person.monotributo_padron or '',
                "tipo_ingreso_bruto": person.l10n_ar_gross_income_type or '',
                "ingreso_bruto": person.l10n_ar_gross_income_number or '',
                "impuestos": list_taxes
              }
        date = fields.Date.today()
        if person.arba_alicuot_ids:
            for item in person.arba_alicuot_ids:
                if item.from_date <= date <= item.to_date:
                    res["alicuotas_pert_ret"] = {
                         "tag_id": item.tag_id.id or 0,
                        "tag_name": item.tag_id.name or '',
                        "alicuota_percepcion": item.alicuota_percepcion or 0,
                        "alicuota_retencion": item.alicuota_retencion or 0,
                    }
        return res
    
    def create(self, **params):
        list = []
        contacts = self.env['res.partner']\
            .search([('vat','=',params['vat'])])
        if not contacts:
            res = {
                    "name": params["name"],
                    "company_type": params["company_type"],
                    "vat": params["vat"],
                    "l10n_latam_identification_type_id": params["l10n_latam_identification_type_id"],
                    "l10n_ar_afip_responsibility_type_id": params["l10n_ar_afip_responsibility_type_id"],
                    "ref": params["ref"] or "",
                    "email": params["email"] or "",
                    "phone": params["phone"] or "",
                    "mobile": params["mobile"] or "",
                    "street": params["direccion"] or "",
                    "street2": params["direccion_1"] or "",
                    "city": params["city"] or "",
                    "street_number": params["street_number"] or "",
                    "street_number2": params["street_number2"] or "",
                    "state_id": params["state_id"] or 0,
                    "zip": params["zip"] or "",
                    "user_id": params["user_id"] or 0,
                    "team_id": params["team_id"] or 0,
                    "property_product_pricelist": params["property_product_pricelist"] or 0,
                    "canal_venta_id": params["canal_venta_id"] or 0,
                    "tipo_entrega_id": params["tipo_entrega_id"] or 0,
                    "zona_id": params["zona_id"] or 0
                  }
            contact = self.env['res.partner'].create(res)
            if params["category_id"]:
                for elements in params["category_id"]:
                    for value in elements.values():
                        list.append(value)
                contact.write({"category_id" : [(6, 0, list)]})
            res["message"] = "se creo el contacto: {contact}"\
                    .format(contact = contact.id)
        else:
            res = {"message": "el contacto ya existe con id: {contact}"\
                .format(contact = contacts.id)}
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": True, "nullable": False},
                "name": {"type":"string", "required": True, "nullable": False},
                "company_type": {"type":"string", "required": True, "nullable": False},
                "l10n_latam_identification_type_id": {"type":"integer", "required": True},
                "l10n_ar_afip_responsibility_type_id": {"type":"integer", "required": False},
                "vat": {"type":"string", "required": True},
                "ref": {"type":"string", "required": False},
                "email": {"type":"string", "required": False},
                "phone": {"type":"string", "required": False},
                "mobile": {"type":"string", "required": False},
                "email": {"type":"string", "required": False},
                "direccion": {"type":"string", "required": False},
                "direccion_1": {"type":"string", "required": False},
                "casa": {"type":"string", "required": False},
                "puerta": {"type":"string", "required": False},
                "city": {"type":"string", "required": False},
                "state_id": {"type":"integer", "required": False},
                "zip": {"type":"string", "required": False},
                "country_id": {"type":"integer", "required": False},
                "etiquetas": {"type":"list",
                              "schema": {"type": "dict",
                                        "schema": {
                                            "id": {"type":"integer", "required": False},
                                            "name": {"type":"string", "required": False}
                                        }
                                }
                             },
                "comercial": {"type":"integer", "required": False},
                "equipo_venta": {"type":"integer", "required": False},
                "tarifa_contacto": {"type":"integer", "required": False},
                "canal_venta": {"type":"integer", "required": False},
                "tipo_entrega": {"type":"integer", "required": False},
                "zona": {"type":"integer", "required": False},
                "estado_afip": {"type":"string", "required": False},
                "ganancias": {"type":"string", "required": False},
                "regimen_ganancias": {"type":"integer", "required": False},
                "responsabilidad_iva": {"type":"integer", "required": False},
                "integrante_sociedad": {"type":"string", "required": False},
                "monotributo": {"type":"string", "required": False},
                "tipo_ingreso_bruto": {"type":"string", "required": False},
                "ingreso_bruto": {"type":"string", "required": False},
                "impuestos": {"type":"list",
                              "schema": {"type": "dict",
                                        "schema": {
                                            "id": {"type":"integer", "required": False},
                                            "name": {"type":"string", "required": False}
                                        }
                                }
                             },
                "alicuotas_pert_ret": {"type":"dict", 
                                       "schema": {
                                           "tag_id":{"type":"integer", "required": False},
                                           "tag_name":{"type":"string", "required": False},
                                           "alicuota_percepcion":
                                           {"type":"float", "required": False},
                                           "alicuota_retencion":
                                           {"type":"float", "required": False}
                                       }}
              }
        return res
    
    def _validator_create(self):
        res = {
                "name": {"type":"string", "required": True},
                "company_type": {"type":"string", "required": True},
                "l10n_latam_identification_type_id": {"type":"integer", "required": True},
                "l10n_ar_afip_responsibility_type_id": {"type":"integer", "required": False},
                "vat": {"type":"string", "required": True},
                "ref": {"type":"string", "required": False},
                "email": {"type":"string", "required": True},
                "phone": {"type":"string", "required": False},
                "mobile": {"type":"string", "required": False},
                "direccion": {"type":"string", "required": True},
                "direccion_1": {"type":"string", "required": False},
                "city": {"type":"string", "required": True},
                "street_number": {"type":"string", "required": True},
                "street_number2": {"type":"string", "required": True},
                "state_id": {"type":"integer", "required": True},
                "zip": {"type":"string", "required": True},
                "country_id": {"type":"integer", "required": True},
                "user_id": {"type":"integer", "required": False},
                "team_id": {"type":"integer", "required": False},
                "property_product_pricelist": {"type":"integer", "required": False},
                "canal_venta_id": {"type":"integer", "required": False},
                "tipo_entrega_id": {"type":"integer", "required": False},
                "zona_id": {"type":"integer", "required": False},
                "category_id": {"type":"list",
                                "schema": {"type": "dict",
                                        "schema": {
                                            "category_id": {"type":"integer", "required": False}
                                                  }
                                          }
                               }
              }
        return res
