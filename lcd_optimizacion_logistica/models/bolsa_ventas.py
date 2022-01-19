# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import datetime
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.http import request
from odoo.addons.website.models import ir_http
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BolsaVentas(models.Model):
    _name = 'bolsa.ventas'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Bolsa de Ventas'

    fecha=fields.Date('Fecha')
    name=fields.Char('Número')
    estado=fields.Selection([('abierta','Abierta'),('en_proceso','En Proceso'),('cerrada','Cerrada')],string='Estado',default='abierta',tracking=True)
    bolsa_lines=fields.One2many('bolsa.ventas.detalle','bolsa_id','Items')

    @api.model
    def create(self, vals):
        creacion_manual=False
        if 'name' not in vals:
            #Asigno nombre por secuencia
            vals['name']=self.env['ir.sequence'].next_by_code('bolsa.ventas')
            creacion_manual=True
        res=super(BolsaVentas, self).create(vals)
        res.bolsa_lines.calcular_defaults()
        if creacion_manual==True:
            #Marco los sale.order con el id de esta bolsa
            ordenes=res.bolsa_lines.mapped('order_line_id.order_id.id')
            print('ordenes:',ordenes)
            self.env['sale.order'].browse(set(ordenes)).write({'bolsa_id':res.id})
        return res

    #Si creo una bolsa manualmente, cargo automaticamente el detalle
    @api.model
    def default_get(self, default_fields):
        values = super(BolsaVentas, self).default_get(default_fields)
        #Para no afectar la creación de bolsa de manera automática, pongo la variable skip_default para que solo se ejecute el default_get por defecto
        if 'skip_default' in self.env.context and self.env.context['skip_default']==True:
            return values
        values['fecha'] =datetime.datetime.today()
        bolsa_pedidos=[]
        ordenes=self.env['sale.order'].search([('bolsa_id','=',False),('pedido_sin_optimizar','=',False)],order="date_order")
        for orden in ordenes:
            bolsa_pedidos.append(orden.id)
        lineas_bolsa=[]
        pedidos=self.env['sale.order'].browse(bolsa_pedidos)
        for line in self.env['sale.order.line'].search([('order_id','in',pedidos.ids)]):
            vals_line={}
            vals_line['order_line_id']=line.id
            vals_line['estado']='pendiente'
            vals_line['pedido']=line.order_id.name
            vals_line['fecha_pedido']=line.order_id.date_order
            vals_line['partner_id']=line.order_id.partner_id.id
            vals_line['direccion']=line.order_id.partner_id.street
            vals_line['latitud']=line.order_id.partner_id.partner_latitude
            vals_line['longitud']=line.order_id.partner_id.partner_longitude
            vals_line['product_id']=line.product_id.id
            vals_line['volumen']=line.product_id.volume
            vals_line['fecha_cierta']=line.order_id.fecha_cierta
            vals_line['categ_id']=line.product_id.categ_id.id
            vals_line['zona_id']=line.order_id.zona_id.id
            vals_line['canal_venta_id']=line.order_id.canal_venta_id.id
            vals_line['tipo_entrega_id']=line.order_id.tipo_entrega_id.id
            lineas_bolsa.append((0, 0, vals_line))
        print('lineas_bolsa:',lineas_bolsa)
#        bolsa_new = self.env['bolsa.ventas'].new({'bolsa_lines':lineas_bolsa})
        values['bolsa_lines']=lineas_bolsa
        print('values:',values)
        return values

    def chequear_bolsa(self):
        #Armo un diccionario de categorias con sus capacidades de fabricacion
        categorias=self.env['product.category'].search([]).read(['id','capacidad_fabricacion'])
        dict_categ={}
        categorias_cant={}
        for item in categorias:
            dict_categ[item['id']]=item['capacidad_fabricacion']
            categorias_cant[item['id']]=0
        #####################################################################
        #Recorro pedidos que no estan en bolsa y chequeo si excede capacidad
        excede_limite=False
        bolsa_pedidos=[]
        ordenes=self.env['sale.order'].search([('bolsa_id','=',False),('pedido_sin_optimizar','=',False)],order="date_order")
        for orden in ordenes:
            bolsa_pedidos.append(orden.id)
            for linea in orden.order_line:
                categorias_cant[linea.product_id.categ_id.id]=categorias_cant[linea.product_id.categ_id.id]+linea.product_uom_qty
                #Si la cantidad de la ov excede la capacidad de fabricacion cierro bolsa
                if categorias_cant[linea.product_id.categ_id.id]>dict_categ[linea.product_id.categ_id.id] and dict_categ[linea.product_id.categ_id.id]!=0:
                    excede_limite=True
                    break
            if excede_limite==True:
                #Si excede límite tengo que crear bolsa
                lineas_bolsa=[]
                pedidos=self.env['sale.order'].browse(bolsa_pedidos)
                for line in self.env['sale.order.line'].search([('order_id','in',pedidos.ids)]):
                    lineas_bolsa.append((0, 0, {'order_line_id': line.id,'estado':'pendiente'}))
                bolsa=self.env['bolsa.ventas'].create({'fecha':datetime.datetime.today(),'name':self.env['ir.sequence'].next_by_code('bolsa.ventas'),'bolsa_lines':lineas_bolsa})
                pedidos.write({'bolsa_id':bolsa.id})
                #Reseteo variables
                excede_limite=False
                bolsa_pedidos=[]
                for item in categorias:
                    categorias_cant[item['id']]=0

        parametro=self.env['ir.config_parameter'].search([('key','=','optimizacion.dias_venta')])
        ultima_bolsa=self.env['bolsa.ventas'].search([],order="fecha desc",limit=1)
        if ultima_bolsa:
            fecha_comparacion=ultima_bolsa.fecha
        else:
            #Si no tengo bolsa para comparar, agarro la orden mas vieja sin bolsa asociada
            orden=self.env['sale.order'].search([('bolsa_id','=',False)],order="date_order",limit=1)
            if orden:
                fecha_comparacion=orden.date_order
            else:
                fecha_comparacion=datetime.datetime.today()
        #Si se excede el límite de fabricación por categoria o se cumple la cantidad de días de bolsa definido, creo nueva bolsa
        print('categorias_cant:',categorias_cant)
        print('dict_categ:',dict_categ)
        print('excede_limite:',excede_limite)
        print('datetime.date.today():',datetime.date.today())
        print('fecha_comparacion:',fecha_comparacion)
        print('parametro.value:',parametro.value)
        if excede_limite or (datetime.date.today()-fecha_comparacion).days>=int(parametro.value):
            lineas_bolsa=[]
            pedidos=self.env['sale.order'].browse(bolsa_pedidos)
            for line in self.env['sale.order.line'].search([('order_id','in',pedidos.ids)]):
                lineas_bolsa.append((0, 0, {'order_line_id': line.id,'estado':'pendiente'}))
            if lineas_bolsa!=[]:
                bolsa=self.env['bolsa.ventas'].create({'fecha':datetime.datetime.today(),'name':self.env['ir.sequence'].next_by_code('bolsa.ventas'),'bolsa_lines':lineas_bolsa})
                pedidos.write({'bolsa_id':bolsa.id})

class BolsaVentasDetalle(models.Model):
    _name = 'bolsa.ventas.detalle'
    _description = 'Detalle de Bolsa de Ventas'

    bolsa_id=fields.Many2one('bolsa.ventas','Bolsa de Ventas')
    order_line_id=fields.Many2one('sale.order.line','Linea de OV')
    pedido=fields.Char(related='order_line_id.order_id.name',string='Pedido',store=True)
    pedido_id=fields.Many2one('sale.order',related='order_line_id.order_id',string='Pedido',store=True)
    mrp_production_id=fields.Many2one('mrp.production','Órden de Producción')
    fecha_pedido=fields.Datetime(related='order_line_id.order_id.date_order',string='Fecha Pedido',store=True)
    partner_id=fields.Many2one('res.partner',related='order_line_id.order_id.partner_id',string='Cliente',store=True)
    direccion=fields.Char(related='order_line_id.order_id.partner_shipping_id.street',string='Dirección',store=True)
    telefono=fields.Char(related='order_line_id.order_id.partner_id.phone',string='Teléfono',store=True)
    celular=fields.Char(related='order_line_id.order_id.partner_id.mobile',string='Celular',store=True)
    latitud=fields.Float(related='order_line_id.order_id.partner_id.partner_latitude',string='Latitud',store=True)
    longitud=fields.Float(related='order_line_id.order_id.partner_id.partner_longitude',string='Longitud',store=True)
    product_id=fields.Many2one('product.product',related='order_line_id.product_id',string='Producto',store=True)
    volumen=fields.Float(related='order_line_id.product_id.volume',string='Volumen',store=True)
    fecha_cierta=fields.Date(related='order_line_id.order_id.fecha_cierta',string='Fecha Cierta',store=True)
    categ_id=fields.Many2one('product.category',related='order_line_id.product_id.categ_id',string='Categoría',store=True)
    zona_id=fields.Many2one('sale.order.zona',related='order_line_id.order_id.zona_id',string='Zona',store=True)
    canal_venta_id=fields.Many2one('sale.order.canal',related='order_line_id.order_id.canal_venta_id',string='Canal de Venta',store=True)
    fecha_canal_venta=fields.Date(string='Fecha Máxima Canal de Venta',store=True,compute='calcular_defaults')
    mayorista=fields.Boolean(string='Mayorista',store=True,compute='calcular_defaults')
    fabricar=fields.Boolean(string='¿Fabricar?',compute='calcular_defaults',store=True)
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega',related='order_line_id.order_id.tipo_entrega_id',string='Tipo Entrega',store=True)
    cantidad=fields.Float(related='order_line_id.product_uom_qty',string='Cantidad',store=True)
    cantidad_a_realizar=fields.Float(string='Cantidad A Realizar',default=0)
    cantidad_realizada=fields.Float(string='Cantidad Realizada',default=0)
    estado=fields.Selection([('pendiente','Pendiente'),('en_proceso','En Proceso'),('optimizado','Optimizado'),('cancelado','Cancelado')],string='Estado',default='pendiente')

    def ignorar(self):
        self.estado='cancelado'

    def calcular_defaults(self):
        print('entro a calcular_defaults')
        producto_fabricable=self.env.ref('mrp.route_warehouse0_manufacture').id
        etiquetas_mayoristas=self.env['ir.config_parameter'].search([('key','=','optimizacion.etiquetas_mayoristas')])
        if etiquetas_mayoristas:
            etiquetas_mayoristas=etiquetas_mayoristas.value.split(',')
        for rec in self:
            if rec.canal_venta_id.dias_maximos:
                rec.fecha_canal_venta=fields.Date.from_string(rec.fecha_pedido)+datetime.timedelta(days=rec.canal_venta_id.dias_maximos)
            else:
                rec.fecha_canal_venta=False
            if etiquetas_mayoristas:
                rec.mayorista=False
                for tag in rec.partner_id.category_id:
                    if tag.id in etiquetas_mayoristas:
                        rec.mayorista=True
                        break
            else:
                rec.mayorista=False
            if rec.product_id.route_ids ==False or (producto_fabricable not in rec.product_id.route_ids.ids):
                rec.fabricar=False
            else:
                rec.fabricar=True

    #Si se modifica la fecha cierta, debo modificarla del pedido y de la optimización también
    @api.onchange('fecha_cierta')
    def onchange_fecha_cierta(self):
        self.order_line_id.order_id.fecha_cierta=self.fecha_cierta
        self.env['optimizacion.logistica.detalle'].search([('bolsa_line_id','=',self.id)]).write({'fecha_cierta':self.fecha_cierta})
        for item in self.bolsa_id.bolsa_lines:
            if item!=self and item.pedido==self.pedido:
                print('entro')
                item.fecha_cierta=self.fecha_cierta

    #Si se modifica la zona, debo modificarla del pedido y de la optimización también
    @api.onchange('zona_id')
    def onchange_zona_id(self):
        self.order_line_id.order_id.zona_id=self.zona_id
        self.env['optimizacion.logistica.detalle'].search([('bolsa_line_id','=',self.id)]).write({'zona_id':self.zona_id.id})
        for item in self.bolsa_id.bolsa_lines:
            print('item:',item)
            print('item.zona_id:',item.zona_id)
            print('self.zona_id:',self.zona_id)
            if item!=self and item.zona_id==self.zona_id:
                print('entro')
                item.zona_id=self.zona_id.id
