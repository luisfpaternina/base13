# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime,date
import base64
import xml.etree.cElementTree as ET


class AccountPaymentGroup(models.Model):
    """ Agrega campos necesarios para aplicar a las reglas de usuario en Recibos de pago clientes y proveedores. """
    _inherit = 'account.payment.group'


    provisional = fields.Boolean("Provisorio", default=False)


    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        """ Oculta el campo provisional para el grupo group_user. """
        res = super(AccountPaymentGroup, self).fields_view_get(
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

    def post(self):
        """ Al validar Recibo pago cliente/proveedor. Se extiende y establece el campo provisorio en True si el origen de la factura contiene diario provisorio """
        create_from_website = self._context.get('create_from_website', False)
        create_from_statement = self._context.get('create_from_statement', False)
        create_from_expense = self._context.get('create_from_expense', False)

        active_ids = self.env.context.get('active_ids')
        move_ids = self.env['account.move'].browse(active_ids)
        for rec in self:
            # TODO if we want to allow writeoff then we can disable this
            # constrain and send writeoff_journal_id and writeoff_acc_id
            if not rec.payment_ids:
                raise ValidationError(_(
                    'You can not confirm a payment group without payment '
                    'lines!'))
            # si el pago se esta posteando desde statements y hay doble
            # validacion no verificamos que haya deuda seleccionada
            if (rec.payment_subtype == 'double_validation' and
                    rec.payment_difference and (not create_from_statement and
                                                not create_from_expense)):
                raise ValidationError(_(
                    'To Pay Amount and Payment Amount must be equal!'))

            writeoff_acc_id = False
            writeoff_journal_id = False
            # if the partner of the payment is different of ht payment group we change it.
            rec.payment_ids.filtered(lambda p : p.partner_id != rec.partner_id).write(
                {'partner_id': rec.partner_id.id})
            # al crear desde website odoo crea primero el pago y lo postea
            # y no debemos re-postearlo
            if not create_from_website and not create_from_expense:
                rec.payment_ids.filtered(lambda x: x.state == 'draft').post()

            counterpart_aml = rec.payment_ids.mapped('move_line_ids').filtered(
                lambda r: not r.reconciled and r.account_id.internal_type in (
                    'payable', 'receivable'))

            # porque la cuenta podria ser no recivible y ni conciliable
            # (por ejemplo en sipreco)
            if counterpart_aml and rec.to_pay_move_line_ids:
                (counterpart_aml + (rec.to_pay_move_line_ids)).reconcile(
                    writeoff_acc_id, writeoff_journal_id)

            rec.state = 'posted'
            if move_ids.journal_id.provisional:
                rec.provisional = True
        return True



    def write(self, vals):
        """ Al Guardar Recibo pago cliente/proveedor. Se extiende y establece el campo provisorio en True si el origen de la factura contiene diario provisorio """
        active_ids = self.env.context.get('active_ids')

        move_ids = self.env['account.move'].browse(active_ids)
        provisional = False
        if move_ids.journal_id.provisional:
            provisional = True
        self.env.cr.execute("SELECT MAX(id) as id FROM account_payment_group")
        if self.env.cr.rowcount:
            res = self.env.cr.dictfetchall()
            for fila in res:
                new_number = fila['id'] + 1
        val ={
            'name': new_number,
            'provisional': provisional,
        }
        vals.update(val)
        res = super(AccountPaymentGroup, self).write(vals)

        return res




class AccountPayment(models.Model):
    _inherit = "account.payment"

    def get_journals_domain(self):
        """
        Obtenemos move_id de contexto y agregamos dominio journal para obtener diarios de pago provisorios o fiscales.

        """
        active_ids = self.env.context.get('move_id')
        move_id = self.env['account.move'].browse(active_ids)

        self.ensure_one()

        domain = [('type', 'in', ('bank', 'cash'))]
        if self.payment_type == 'inbound':
            domain.append(('at_least_one_inbound', '=', True))
            if move_id.journal_id.provisional:
                """  agregamos dominio journal para obtener diarios de pago provisorios """
                domain.append(('provisional', '=', True))
            else:
                """  agregamos dominio journal para obtener diarios de pago fiscales """
                domain.append(('provisional', '=', False))
        # Al final dejamos que para transferencias se pueda elegir
        # cualquier sin importar si tiene outbound o no
        # else:
        elif self.payment_type == 'outbound':
            domain.append(('at_least_one_outbound', '=', True))
            if move_id.journal_id.provisional:
                """  agregamos dominio journal para obtener diarios de pago provisorios """
                domain.append(('provisional', '=', True))
            else:
                """  agregamos dominio journal para obtener diarios de pago fiscales """
                domain.append(('provisional', '=', False))

        return domain






