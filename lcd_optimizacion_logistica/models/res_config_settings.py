# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dias_de_venta = fields.Integer('Días de Venta', config_parameter='optimizacion.dias_venta')
    maximo_fabricacion_mayoristas = fields.Integer('Máximo de Fabricación Mayoristas (0-100%)', config_parameter='optimizacion.maximo_fabricacion_mayoristas')
    etiquetas_mayoristas = fields.Many2many('res.partner.category',string='Etiquetas de Mayoristas', compute="_compute_etiquetas_fields", inverse="_inverse_etiquetas_fields_str")
    etiquetas_mayoristas_str = fields.Char(string='Etiquetas de Mayoristas', config_parameter='optimizacion.etiquetas_mayoristas')

    @api.depends('etiquetas_mayoristas_str')
    def _compute_etiquetas_fields(self):
        """ As config_parameters does not accept m2m field,
            we get the fields back from the Char config field, to ease the configuration in config panel """
        for setting in self:
            if setting.etiquetas_mayoristas_str:
                names = setting.etiquetas_mayoristas_str.split(',')
                setting.etiquetas_mayoristas = self.env['res.partner.category'].search([('id', 'in', names)])
            else:
                setting.etiquetas_mayoristas = None

    def _inverse_etiquetas_fields_str(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting.etiquetas_mayoristas:
                setting.etiquetas_mayoristas_str = ','.join([str(elem) for elem in setting.etiquetas_mayoristas.ids])
            else:
                setting.etiquetas_mayoristas_str = ''
