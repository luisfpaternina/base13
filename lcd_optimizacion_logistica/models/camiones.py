# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class LcdCamion(models.Model):
    _name = 'lcd.camion'
    _rec_name = 'placa'

    placa=fields.Char('Patente')
    tipo_vehiculo=fields.Many2one('lcd.tipo_vehiculo','Tipo de Vehículo')
    capacidad=fields.Integer('Capacidad (m3)')
    contratista_id=fields.Many2one('res.partner','Contratista')
    viajes_dia=fields.Integer('Viajes por Día')

class LcdTipoVehiculo(models.Model):
    _name = 'lcd.tipo_vehiculo'

    name=fields.Char('Nombre')
