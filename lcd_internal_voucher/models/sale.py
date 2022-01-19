# -*- coding: utf-8 -*-
import pdb

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime,date
import base64
import xml.etree.cElementTree as ET


class SaleOrder(models.Model):
    """ Agrega campo provisorio en Presupuesto Venta / Pedido Venta. """
    _inherit = ['sale.order']

    provisional = fields.Boolean('Provisorio',groups='lcd_internal_voucher.group_voucher_user')


    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """ Oculta el campo provisional para el grupo group_user. """
        res = super(SaleOrder, self).fields_view_get(
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


    def _prepare_invoice(self):
        """
        Extiende funcion y agrega en el caso de Order marcada como provisoria, el Diario de venta provisorio.
        """
        self.ensure_one()
        # ensure a correct context for the _get_default_journal method and company-dependent fields
        self = self.with_context(default_company_id=self.company_id.id, force_company=self.company_id.id)
        if self.provisional:
            journal1 = self.env['account.journal'].search([('provisional', '=', True),('type','=','sale')])
            journal = journal1[0]
        else:
            journal2 = self.env['account.journal'].search([('provisional', '=', False), ('type', '=', 'sale')])
            journal = journal2[0]
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals




class SaleOrderLine(models.Model):
    """ Linea de SO se agrega funcionalidad para determinar que impuesto aplicar en caso de comprobante interno. """
    _inherit = 'sale.order.line'


    def _prepare_invoice_line(self):
        """
        Extiende funcion y agrega en el caso de Order marcada como provisoria, la linea de impuesto IVA no gravado.
        """
        self.ensure_one()
        if self.order_id.provisional:
            tax_id = self.env['account.tax'].search([('name','=','IVA No Gravado'),('type_tax_use','=','sale')])
            tax_ids = tax_id
        else:
            tax_ids = [(6, 0, self.tax_id.ids)]
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': tax_ids,
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.display_type:
            res['account_id'] = False
        return res

















