from odoo import api, fields, models
import xml.etree.cElementTree as ET


class AgedPartnerBalanceWizard2(models.TransientModel):
    """ AGREGA CAMPOS A PARTNER BALANCE. """
    _inherit = "general.ledger.report.wizard"

    provisional2 = fields.Boolean("Provisorio", default=False)
    fiscal2 = fields.Boolean("Fiscal", default=False)


    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """ Oculta el campo provisional2 para el grupo group_user. """
        res = super(AgedPartnerBalanceWizard2, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        group_user = self.user_has_groups("lcd_internal_voucher.group_voucher_user")
        group_manager = self.user_has_groups("lcd_internal_voucher.group_voucher_admin")
        if not group_manager and (group_user):
            if view_type in ["form"]:
                root = ET.fromstring(res["arch"])
                for el in root.iter("field"):
                    if el.attrib.get("name") in ["provisional2"]:
                        el.attrib.update(
                            {
                                "modifiers": '{"invisible": [["id", "!=", 0]]}',
                            }
                        )
                res.update({"arch": ET.tostring(root, encoding="utf8", method="xml")})
        return res
