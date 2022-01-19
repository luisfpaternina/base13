# -*- coding: utf-8 -*-
import pdb

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime,date
import base64
from odoo.tools.float_utils import float_compare
import xml.etree.cElementTree as ET


class PurchaseOrder(models.Model):
    """ Agrega campo provisorio en Presupuesto Compra / Pedido Compra. """
    _inherit = 'purchase.order'

    provisional = fields.Boolean('Provisorio', groups='lcd_internal_voucher.group_voucher_user')


    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """ Oculta el campo provisional para el grupo group_user. """
        res = super(PurchaseOrder, self).fields_view_get(
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



class PurchaseOrderLine(models.Model):
    """ Linea de PO se agrega funcionalidad para determinar que diario e impuesto aplicar en caso de comprobante interno. """
    _inherit = 'purchase.order.line'


    def _prepare_account_move_line(self, move):
        """
        Extiende funcion y agrega en el caso de Order marcada como provisoria, la linea de impuesto IVA no gravado.
        También agrega en la Order marcada como provisoria, el Diario de venta marcado como provisorio.

        """
        self.ensure_one()
        if self.product_id.purchase_method == 'purchase':
            qty = self.product_qty - self.qty_invoiced
        else:
            qty = self.qty_received - self.qty_invoiced

        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
            qty = 0.0
        if self.order_id.provisional:
            journal1 = self.env['account.journal'].search([('provisional', '=', True), ('type', '=', 'purchase')])
            journal = journal1[0]
            tax_id = self.env['account.tax'].search([('name', '=', 'IVA No Gravado'), ('type_tax_use', '=', 'purchase')])
            tax_ids = tax_id
        else:
            journal2 = self.env['account.journal'].search([('provisional', '=', False), ('type', '=', 'purchase')])
            journal = journal2[0]
            tax_ids = [(6, 0, self.taxes_id.ids)]
        move_data = {
            'journal_id': journal,
        }
        move.write(move_data)


        return {
            'name': '%s: %s' % (self.order_id.name, self.name),
            'move_id': move.id,
            'currency_id': move.currency_id.id,
            'purchase_line_id': self.id,
            'date_maturity': move.invoice_date_due,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'partner_id': move.commercial_partner_id.id,
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'tax_ids': tax_ids,
            'display_type': self.display_type,
        }


















