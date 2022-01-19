# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ManualDelivery(models.TransientModel):
    _inherit = "manual.delivery"

    @api.model
    def default_get(self, fields):
        print('entro aqui:',self.env.context)
        if 'active_model' in self.env.context:
            res = super().default_get(fields)
            return res
