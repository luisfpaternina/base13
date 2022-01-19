# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime,date
import base64
import xml.etree.cElementTree as ET
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    """ Se extiende campos necesarios para aplicar a las reglas de usuario. """
    _order = "id desc"
    _inherit = ['account.move']

    provisional = fields.Boolean('Provisorio',groups='lcd_internal_voucher.group_voucher_user')


    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """ Oculta el campo provisional para el grupo group_user. """
        res = super(AccountMove, self).fields_view_get(
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


    def action_post(self):
        """ Valida que el Diario seleccionado en Factura sea provisorio si la Orden de origen es provisorio """
        """ Valida que el Diario seleccionado en Factura sea Fiscal si la Orden de origen es Fiscal """
        if self.filtered(lambda x: x.journal_id.post_at == 'bank_rec').mapped('line_ids.payment_id').filtered(lambda x: x.state != 'reconciled'):
            raise UserError(_("A payment journal entry generated in a journal configured to post entries only when payments are reconciled with a bank statement cannot be manually posted. Those will be posted automatically after performing the bank reconciliation."))
        if self.env.context.get('default_type'):
            context = dict(self.env.context)
            del context['default_type']
            self = self.with_context(context)
        if self.invoice_origin:
            if self.journal_id.type == 'sale':
                order = self.env['sale.order'].search([('name','=',self.invoice_origin)])
            elif self.journal_id.type == 'purchase':
                order = self.env['purchase.order'].search([('name', '=', self.invoice_origin)])
            if order.provisional and self.journal_id.provisional == False:
                raise UserError(
                    _('Error: Diario no admitido para comprobantes internos.'))
            elif self.journal_id.provisional and order.provisional == False:
                raise UserError(
                    _('Error: Diario no admitido para comprobantes Fiscal.'))

        return self.post()



class AccountMoveLine(models.Model):
    """ Agrega modelo necesario para aplicar a las reglas de usuario. """
    _order = "id desc"
    _inherit = ['account.move.line']















