# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import datetime
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fecha_cierta=fields.Date('Fecha Cierta')
    canal_venta_id=fields.Many2one('sale.order.canal','Canal de Venta',ondelete='restrict')
    pedido_sin_optimizar=fields.Boolean('Pedido sin Optimizar')
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega','Tipo de Entrega',ondelete='restrict')
    zona_id=fields.Many2one('sale.order.zona','Zona',ondelete='restrict')
    bolsa_id=fields.Many2one('bolsa.ventas','Bolsa de Ventas')

    @api.onchange('partner_id','partner_shipping_id')
    def onchange_partner_id_lcd(self):
        if self.partner_id.tipo_entrega_id:
            self.tipo_entrega_id=self.partner_id.tipo_entrega_id.id
        if self.partner_id.canal_venta_id:
            self.canal_venta_id=self.partner_id.canal_venta_id.id
#        if self.partner_id.zona_id:
#            self.zona_id=self.partner_id.zona_id.id
        if self.partner_shipping_id:
            zip_code=self.partner_shipping_id.zip
        else:
            zip_code=self.partner_id.zip
        print('zip_code:',zip_code)
        zip_code_obj=self.env['sale.order.zip'].search([('name','=',zip_code)])
        if zip_code_obj:
            self.zona_id=zip_code_obj.zona_id.id
        else:
            self.zona_id=self.env.ref('lcd_optimizacion_logistica.sale_order_zona_sin_zona').id

    def action_confirm(self):
        if not self.zona_id:
            raise UserError('Debe definir Zona')
        self.write({'manual_delivery':True})
        res = super(SaleOrder, self).action_confirm()
        self.env['bolsa.ventas'].with_context(skip_default=True).chequear_bolsa()
        return res 

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        #Verifico si hay que cancelar bolsas detalle
        print('Verifico si hay que cancelar bolsas detalle:',self.env['bolsa.ventas.detalle'].search([('id','in',self.order_line.ids)]))
        for bolsa_det in self.env['bolsa.ventas.detalle'].search([('id','in',self.order_line.ids)]):
            bolsa_det.write({'estado':'cancelado'})
            #Verifico si hay que cancelar optimizacion detalle
            print('Verifico si hay que cancelar optimizacion detalle:',self.env['optimizacion.logistica.detalle'].search([('bolsa_line_id','=',bolsa_det.id)]))
            for opt_det in self.env['optimizacion.logistica.detalle'].search([('bolsa_line_id','=',bolsa_det.id)]):
                opt_det.write({'estado':'cancelado'})
                bolsa_det.write({'cantidad_a_realizar':bolsa_det.cantidad_a_realizar-opt_det.cantidad_a_realizar})
        #Verifico si hay que cancelar ordenes de fabricación que no estén terminadas o en proceso
        #Verifico si hay que cancelar rutas y horarios
        return res 

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bolsa_detalle_id=fields.Many2one('bolsa.ventas.detalle','Línea bolsa detalle')

class SaleOrderCanal(models.Model):
    _name = 'sale.order.canal'
    _description = 'Canal de Venta'

    name=fields.Char('Nombre',required=True)
    codigo=fields.Char('Código',required=True)
    dias_maximos=fields.Integer('Días Máximos')

    _sql_constraints = [
        ('canal_codigo_uniq', 'UNIQUE(codigo)', 'El código de canal debe ser único')
    ]

class SaleOrderTipoEntrega(models.Model):
    _name = 'sale.order.tipo_entrega'
    _description = 'Tipo de Entrega'

    name=fields.Char('Nombre',required=True)
    codigo=fields.Char('Código',required=True)
    tiempo_entrega=fields.Integer('Tiempo de Entrega (minutos)')

    _sql_constraints = [
        ('tipo_entrega_codigo_uniq', 'UNIQUE(codigo)', 'El código de tipo de entrega debe ser único')
    ]

class SaleOrderZona(models.Model):
    _name = 'sale.order.zona'
    _description = 'Zona'

    name=fields.Char('Nombre',required=True)
    codigo=fields.Char('Código',required=True)
    codigos_postales=fields.One2many('sale.order.zip','zona_id','Códigos Postales')

    _sql_constraints = [
        ('zona_codigo_uniq', 'UNIQUE(codigo)', 'El código de zona debe ser único')
    ]

    def unlink(self):
        if self.id==self.env.ref('lcd_optimizacion_logistica.sale_order_zona_sin_zona').id:
            raise UserError("No tiene permitido eliminar la Zona sin Definir")
        return super().unlink()

class SaleOrderZip(models.Model):
    _name = 'sale.order.zip'

    name=fields.Char('Código Postal',required=True)
    zona_id=fields.Many2one('sale.order.zona','Zona')

    _sql_constraints = [
        ('zip_name_uniq', 'UNIQUE(name)', 'El código postal debe ser único')
    ]
