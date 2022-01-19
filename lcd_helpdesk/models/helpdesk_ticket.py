from odoo import models, fields, api, _

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def message_new(self, msg, custom_values=None):
        custom_values={}
        contacto=self.env["helpdesk.ticket.type"].search([("name","=","Contacto")],limit = 1)
        equipo=self.env["helpdesk.ticket.team"].search([("name","=","Atención al cliente")],limit = 1)
        if msg.get("to")=='defensaconsumidor@lacardeuse.com.ar':
            canal=self.env["helpdesk.ticket.channel"].search([("name","=","Defensa Consumidor")],limit = 1)
            custom_values["priority"] = "3"
            custom_values["type_id"] = contacto.id
            custom_values["channel_id"] = canal.id
            custom_values["team_id"] = equipo.id
        elif msg.get("to")=='atencionalcliente@lacardeuse.com.ar':
            canal=self.env["helpdesk.ticket.channel"].search([("name","=","Email")],limit = 1)
            custom_values["type_id"] = contacto.id
            custom_values["channel_id"] = canal.id
            custom_values["team_id"] = equipo.id
        ticket = super().message_new(msg, custom_values=custom_values)
        return ticket
