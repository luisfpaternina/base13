{
    'name': 'Post La Cardeuse',
    'version': '1.0',
    'description': 'This module create API',
    'author': 'Nybble Group',
    'website': '',
    'license': 'LGPL-3',
    'category': 'API',
    'depends': [
        'base_rest',
        'sale_management'
    ],
    'data': [
        "views/sale_order_view.xml"
    ],
    "external_dependencies": {"python": ['cryptography'], "bin": []},
    'auto_install': True,
    'application': True,
}