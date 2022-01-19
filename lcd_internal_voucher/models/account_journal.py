# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import base64
import xml.etree.cElementTree as ET


class AccountJournal(models.Model):
    """ Agrega campos necesarios para aplicar a las reglas de usuario. """
    _order = "id desc"
    _inherit = ['account.journal']


    provisional = fields.Boolean('Provisorio',groups='lcd_internal_voucher.group_voucher_user')



    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """ Oculta el campo provisional para el grupo group_user. """
        res = super(AccountJournal, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        group_user = self.user_has_groups("lcd_internal_voucher.group_voucher_user")
        group_manager = self.user_has_groups("lcd_internal_voucher.group_voucher_admin")
        if not group_manager and (group_user):
            if view_type in ["form"]:
                root = ET.fromstring(res["arch"])
                for el in root.iter("field"):
                    if el.attrib.get("name") in ["provisional"]:
                        el.attrib.update(
                            {
                                "modifiers": '{"invisible": [["id", "!=", 0]]}',
                            }
                        )
                res.update({"arch": ET.tostring(root, encoding="utf8", method="xml")})
        return res
