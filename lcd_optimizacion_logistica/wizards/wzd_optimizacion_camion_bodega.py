# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class WzdOptimizacionCamionBodega(models.TransientModel):
    _name = 'lcd.wzd_optimizacion_camion_bodega'

    bodega_id=fields.Many2one('lcd.bodega','Bodega')
    camion_id=fields.Many2one('lcd.camion','Camión')

    def asignar(self):
        self.env['optimizacion.logistica.detalle'].search([('id','in',self.env.context['active_ids']),('estado','=','borrador')]).write({'camion_id':self.camion_id.id,'bodega_id':self.bodega_id.id})
        return {'type': 'ir.actions.client','tag': 'reload',}
