from odoo import http
from odoo.http import request
from cryptography.fernet import Fernet


class Session(http.Controller):
    
    @http.route('/web/session/authenticate/security', type='json', auth="none")
    def authenticate(self, db, login, encrpt_message, base_location=None):
        key = open("/home/odoo/src/user/api_lcd/pass.key", "rb").read()
        f = Fernet(key)
        password = f.decrypt(encrpt_message.encode())
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()