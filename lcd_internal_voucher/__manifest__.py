# -*- coding: utf-8 -*-
{
    'name': 'lcd_internal_voucher',
    'shortdesc': 'Nybble Comprobantes Internos',
    'version': '1.04',
    'summary': 'Comprobantes  Internos',
    'sequence': 1,
    'description': """
Comprobantes Internos:
======================
Módulo que permite manejo de grupos de usuarios, dando acceso a documentos fiscales o provisorios. Se extiende a Diarios, Facturas(recibos de venta/compra), Reportes Contables, como también a Presupuestos / Pedidos y Entregas / Recepciones .
    """,
    'category': 'Voucher',
    'website': 'http://www.nybblegroup.com/',
    'images': ['static/src/img/icon.png'],
    'author': 'Federico Rosales',
    'depends': ['base', 'l10n_ar', 'l10n_ar_afipws_fe', 'l10n_ar_account_withholding', 'account', "sale", 'base_address_city', 'l10n_ar_reports', "date_range", "report_xlsx"
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'views/account_journal_view.xml',
        'views/account_vat_ledger.xml',
        'wizard/aged_partner_balance_wizard_view.xml',
        'views/account_payment_group_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/stock_picking_view.xml',
        'views/account_move_view.xml',

    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    # 'post_init_hook': '_auto_install_l10n',
}
