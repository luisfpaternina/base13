# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons.nybble_gmap_functions.models import gmaps
_logger = logging.getLogger(__name__)


class RutasHorarios(models.Model):
    _name = 'lcd.rutas_horarios'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Rutas y Horarios'

    name=fields.Char('Número de Ruta')
    camion_id=fields.Many2one('lcd.camion','Camión')
    fecha_despacho=fields.Date('Fecha Despacho')
    bodega_id=fields.Many2one('lcd.bodega','Bodega')
    optimizacion_id=fields.Many2one('optimizacion.logistica','Optimización')
    estado=fields.Selection([('borrador','Borrador'),('en_proceso','En Proceso'),('terminado','Terminado')],'Estado')
    items=fields.One2many('lcd.rutas_horarios_detalle','ruta_id')
    items_group=fields.One2many('lcd.rutas_horarios_detalle_group','ruta_id')
    warnings=fields.Text('Advertencias')

    @api.model
    def create(self, vals):
        #Asigno nombre por secuencia
        vals['name']=self.env['ir.sequence'].next_by_code('lcd.rutas_horarios')
        return super(RutasHorarios, self).create(vals)

    def calcular_ruta(self):
        self.items_group.unlink()
        api_key=self.env['ir.config_parameter'].search([('key','=','web_google_maps.api_key')])
        if not api_key:
            raise UserError('Debe establecer un api_key para calcular las rutas')
        else:
            api_key=api_key.value
        print('api_key:',api_key)
        if not self.env.user.company_id.partner_id.partner_latitude or not self.env.user.company_id.partner_id.partner_longitude:
            raise UserError('Debe establecer la ubicación de la compañia')
        direccion_inicio=str(self.env.user.company_id.partner_id.partner_latitude)+','+str(self.env.user.company_id.partner_id.partner_longitude)
        direcciones=[]
        direcciones_sin_coordenadas=[]
        warnings=''
        #Creo listado de direcciones por coordenadas, si alguna línea no tiene coordenadas la ignoro y luego muestro la advertencia
        pedidos=[]
        for linea in self.items:
            if not linea.latitud or not linea.longitud:
                direcciones_sin_coordenadas.append(linea.direccion)
            if str(linea.latitud)+','+str(linea.longitud) not in direcciones:
                direcciones.append(str(linea.latitud)+','+str(linea.longitud))
            vals_pedido=(0,0,{'ruta_id':self.id,'sequence':1000,'pedido':linea.pedido,'pedido_id':linea.pedido_id.id, 'partner_id':linea.partner_id.id, 'direccion':linea.direccion, 'telefono':linea.telefono, 'celular':linea.celular, 'zona_id':linea.zona_id.id, 'tipo_entrega_id':linea.tipo_entrega_id.id,'latitud':linea.latitud,'longitud':linea.longitud})
            if vals_pedido not in pedidos:
                pedidos.append(vals_pedido)
        #Creo grupos por pedido
        self.write({'items_group':pedidos})
        print('direcciones:',direcciones)
        direccion_fin=gmaps.distancia_mas_larga(api_key=api_key,punto_inicio=[direccion_inicio],lista_puntos=direcciones)
        print('direccion_fin:',direccion_fin)
        orden=gmaps.mejor_ruta(api_key=api_key,punto_inicio=direccion_inicio,punto_fin=direccion_fin,lista_puntos=direcciones)
        print('orden:',orden)
        #Asigno secuencia y creo grupos por dirección
        for item in orden:
            latitud,longitud=item[1].split(',')
            self.env['lcd.rutas_horarios_detalle_group'].search([('latitud','=',float(latitud)),('longitud','=',float(longitud)),('ruta_id','=',self.id)]).write({'sequence':item[0]})
            self.env['lcd.rutas_horarios_detalle'].search([('latitud','=',float(latitud)),('longitud','=',float(longitud)),('ruta_id','=',self.id)]).write({'sequence':item[0]})

        print('########################')
        if direcciones_sin_coordenadas!=[]:
            print('direcciones_sin_coordenadas:',direcciones_sin_coordenadas)
            warnings+="Las siguientes direcciones no entraron en la optimización de rutas por no poseer coordenadas:<br>"
            print('warnings1:',warnings)
            for direccion in direcciones_sin_coordenadas:
                warnings+=direccion+"<br>"
                print('warnings2:',warnings)
            print('warnings3:',warnings)
            self.warnings='<font style="color: rgb(207, 36, 21);">'+warnings+'==========================<br></font>'
        self.change_sequence()
    @api.onchange('items_group')
    def change_sequence(self):
#        print('entro:',self.items_group.sequence)
 #       print('entro:',self.ruta_id.items.filtered(lambda v: v.pedido==self.pedido))
  #      for item in self.ruta_id.items.filtered(lambda v: v.pedido==self.pedido):
   #         print('item:',item)
    #        print('item.sequence:',item.sequence)
     #       item.sequence=self.sequence
        print('entro a onchage')
        for item in self.items_group:
            for itemdet in self.items.filtered(lambda v: v.pedido==item.pedido):
                itemdet.sequence=item.sequence


class RutasHorariosDetalleGroup(models.Model):
    _name = 'lcd.rutas_horarios_detalle_group'
    _description = 'Detalle de Rutas y Horarios Agrupado, esto va a permitir mover el orden de entrega de la mercadería por domicilio de pedido'

    ruta_id=fields.Many2one('lcd.rutas_horarios')
    sequence=fields.Integer('Secuencia')
    pedido=fields.Char(string='Pedido')
    pedido_id=fields.Many2one('sale.order',string='Pedido')
    partner_id=fields.Many2one('res.partner',string='Cliente')
    direccion=fields.Char(string='Dirección')
    telefono=fields.Char(string='Teléfono')
    celular=fields.Char(string='Celular')
    zona_id=fields.Many2one('sale.order.zona',string='Zona')
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega',string='Tipo Entrega')
    latitud=fields.Float(string='Latitud')
    longitud=fields.Float(string='Longitud')

class RutasHorariosDetalle(models.Model):
    _name = 'lcd.rutas_horarios_detalle'
    _description = 'Detalle de Rutas y Horarios'

    ruta_id=fields.Many2one('lcd.rutas_horarios')
    sequence=fields.Integer('Secuencia')
    optimizacion_det_id=fields.Many2one('optimizacion.logistica.detalle','Detalle Optimización')
    order_line_id=fields.Many2one('sale.order.line',related='optimizacion_det_id.bolsa_line_id.order_line_id',string='Linea de OV')
    pedido=fields.Char(related='order_line_id.order_id.name',string='Pedido')
    pedido_id=fields.Many2one('sale.order',related='order_line_id.order_id',string='Pedido')
    fecha_pedido=fields.Datetime(related='order_line_id.order_id.date_order',string='Fecha Pedido')
    partner_id=fields.Many2one('res.partner',related='order_line_id.order_id.partner_id',string='Cliente')
    direccion=fields.Char(related='order_line_id.order_id.partner_shipping_id.street',string='Dirección')
    telefono=fields.Char(related='order_line_id.order_id.partner_id.phone',string='Teléfono')
    celular=fields.Char(related='order_line_id.order_id.partner_id.mobile',string='Celular')
    product_id=fields.Many2one('product.product',related='order_line_id.product_id',string='Producto')
    volumen=fields.Float(related='order_line_id.product_id.volume',string='Volumen')
    cantidad=fields.Float('Cantidad')
    fecha_cierta=fields.Date(related='order_line_id.order_id.fecha_cierta',string='Fecha Cierta')
    categ_id=fields.Many2one('product.category',related='order_line_id.product_id.categ_id',string='Categoría')
    zona_id=fields.Many2one('sale.order.zona',related='order_line_id.order_id.zona_id',string='Zona')
    canal_venta_id=fields.Many2one('sale.order.canal',related='order_line_id.order_id.canal_venta_id',string='Canal de Venta')
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega',related='order_line_id.order_id.tipo_entrega_id',string='Tipo Entrega')
    latitud=fields.Float(related='optimizacion_det_id.latitud',string='Latitud',store=True)
    longitud=fields.Float(related='optimizacion_det_id.longitud',string='Longitud',store=True)
    color=fields.Integer('Color')
    estado=fields.Selection([('pendiente','Pendiente'),('en_proceso','En Proceso'),('confirmado','Confirmado'),('despachado','Despachado'),('reprogramacion','Reprogramación'),('terminado','Terminado'),('cancelado','Cancelado')],'Estado')
