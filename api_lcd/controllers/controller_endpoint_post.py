from odoo.addons.base_rest.controllers import main


class PostApi(main.RestController):
    _collection_name = "contact.services.private.services"
    _root_path = "/post_api/"
    _default_auth = "user"