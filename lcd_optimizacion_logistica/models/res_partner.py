# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    canal_venta_id=fields.Many2one('sale.order.canal','Canal de Venta')
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega','Tipo de Entrega')
    zona_id=fields.Many2one('sale.order.zona','Zona')
