# © 2016 Julien Coux (Camptocamp)
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import calendar
import datetime
import operator

from odoo import _, api, models
from odoo.tools import float_is_zero


class GeneralLedgerReport(models.AbstractModel):
    """ Se extiende para obtener filtros de busqueda en la función _get_report_values. """
    _inherit = "report.account_financial_report.general_ledger"


    def _get_report_values(self, docids, data):
        """ Se agregan filtros para el listar Mayor(Estado de cuenta) Cliente/Proveedor que identifiquen  provisorios, fiscales y consolidado. """
        wizard_id = data["wizard_id"]
        company = self.env["res.company"].browse(data["company_id"])
        company_id = data["company_id"]
        date_to = data["date_to"]
        date_from = data["date_from"]
        partner_ids = data["partner_ids"]
        if not partner_ids:
            filter_partner_ids = False
        else:
            filter_partner_ids = True
        account_ids = data["account_ids"]
        analytic_tag_ids = data["analytic_tag_ids"]
        cost_center_ids = data["cost_center_ids"]
        show_partner_details = data["show_partner_details"]
        hide_account_at_0 = data["hide_account_at_0"]
        foreign_currency = data["foreign_currency"]
        only_posted_moves = data["only_posted_moves"]
        unaffected_earnings_account = data["unaffected_earnings_account"]
        fy_start_date = data["fy_start_date"]
        extra_domain = data["domain"]
        # Busco Diario(Journal) provisiorio o Fiscal y agrego domain
        wz_id = self.env['general.ledger.report.wizard'].search([('id', '=', wizard_id)])
        if wz_id.provisional2:
            extra_domain += [("move_id.journal_id.provisional", "=", "True")] + data["domain"]
        elif wz_id.fiscal2:
            extra_domain += [("move_id.journal_id.provisional", "!=", "True")] + data["domain"]
        gen_ld_data, partners_data, partners_ids = self._get_initial_balance_data(
            account_ids,
            partner_ids,
            company_id,
            date_from,
            foreign_currency,
            only_posted_moves,
            unaffected_earnings_account,
            fy_start_date,
            analytic_tag_ids,
            cost_center_ids,
            extra_domain,
        )
        centralize = data["centralize"]
        (
            gen_ld_data,
            accounts_data,
            partners_data,
            journals_data,
            full_reconcile_data,
            taxes_data,
            tags_data,
            rec_after_date_to_ids,
        ) = self._get_period_ml_data(
            account_ids,
            partner_ids,
            company_id,
            foreign_currency,
            only_posted_moves,
            date_from,
            date_to,
            partners_data,
            gen_ld_data,
            partners_ids,
            analytic_tag_ids,
            cost_center_ids,
            extra_domain,
        )
        general_ledger = self._create_general_ledger(
            gen_ld_data,
            accounts_data,
            show_partner_details,
            rec_after_date_to_ids,
            hide_account_at_0,
        )
        if centralize:
            for account in general_ledger:
                if account["centralized"]:
                    centralized_ml = self._get_centralized_ml(account, date_to)
                    account["move_lines"] = centralized_ml
                    account["move_lines"] = self._recalculate_cumul_balance(
                        account["move_lines"],
                        gen_ld_data[account["id"]]["init_bal"]["balance"],
                        rec_after_date_to_ids,
                    )
                    if account["partners"]:
                        account["partners"] = False
                        del account["list_partner"]
        general_ledger = sorted(general_ledger, key=lambda k: k["code"])
        return {
            "doc_ids": [wizard_id],
            "doc_model": "general.ledger.report.wizard",
            "docs": self.env["general.ledger.report.wizard"].browse(wizard_id),
            "foreign_currency": data["foreign_currency"],
            "company_name": company.display_name,
            "company_currency": company.currency_id,
            "currency_name": company.currency_id.name,
            "date_from": data["date_from"],
            "date_to": data["date_to"],
            "only_posted_moves": data["only_posted_moves"],
            "hide_account_at_0": data["hide_account_at_0"],
            "show_analytic_tags": data["show_analytic_tags"],
            "show_cost_center": data["show_cost_center"],
            "general_ledger": general_ledger,
            "accounts_data": accounts_data,
            "partners_data": partners_data,
            "journals_data": journals_data,
            "full_reconcile_data": full_reconcile_data,
            "taxes_data": taxes_data,
            "centralize": centralize,
            "tags_data": tags_data,
            "filter_partner_ids": filter_partner_ids,
        }
